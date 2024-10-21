import json
import sys


def sync_properties(src_data, tgt_data):
    """Sync properties from src_data to tgt_data, skipping specified keys."""
    for key, value in src_data.items():
        # Skip keys that should not be modified
        if key in ["@vocab", "@type", "@id"]:
            continue

        # If the value is a dictionary, recurse
        if isinstance(value, dict):
            tgt_data[key] = sync_properties(value, tgt_data.get(key, {}))
        elif isinstance(value, list):
            # Handle list items based on whether they contain dictionaries with '@id'
            if all(isinstance(item, dict) and '@id' in item for item in value):
                tgt_data_dict = {item['@id']: item for item in tgt_data.get(key, []) if isinstance(item, dict) and '@id' in item}

                for item in value:
                    tgt_data_dict[item['@id']] = sync_properties(item, tgt_data_dict.get(item['@id'], {}))
                tgt_data[key] = list(tgt_data_dict.values())
            else:
                # Append or update items in the list
                tgt_data[key] = [item if not isinstance(item, dict) or '@type' not in item else next(
                    (tgt_item.update(item) or tgt_item for tgt_item in tgt_data.get(key, []) if tgt_item.get('@type') == item['@type']),
                    item
                ) for item in value]
        else:
            # Update the value in the target
            tgt_data[key] = value

    return tgt_data


def main(src_file, tgt_file):
    # Load source JSON data
    with open(src_file) as f:
        src_data = json.load(f)

    # Load target JSON data
    with open(tgt_file) as f:
        tgt_data = json.load(f)

    print(f'Test synced properties from {src_file} to {tgt_file}')

    # Sync properties
    target_data = sync_properties(src_data, tgt_data)
    print(target_data)
    # Write the updated target data back to the file
    with open(tgt_file, 'w') as f:
        json.dump(target_data, f, indent=2)

    print(f'Successfully synced properties from {src_file} to {tgt_file}')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sync_json.py <src_file> <tgt_file>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
