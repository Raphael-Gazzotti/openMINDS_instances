import json
import sys


def sync_properties(src_data, tgt_data):
    """Sync properties from src_data to tgt_data, skipping specified keys."""
    for key, value in src_data.items():
        # Skip special keys
        if key in ["@id", "@type", "@vocab"]:
            continue

        # If the value is a dictionary, recurse
        if isinstance(value, dict):
            tgt_data[key] = tgt_data.get(key, {})
            tgt_data[key] = sync_properties(value, tgt_data[key])
        elif isinstance(value, list):
            # Handle list synchronization
            tgt_data[key] = tgt_data.get(key, [])
            tgt_data_dict = {item['@id']: item for item in tgt_data[key] if isinstance(item, dict) and '@id' in item}

            for item in value:
                if isinstance(item, dict) and '@id' in item:
                    if item['@id'] in tgt_data_dict:
                        # Update properties from src_data to tgt_data_dict[item['@id']]
                        tgt_data_dict[item['@id']] = sync_properties(item, tgt_data_dict[item['@id']])

            # After processing, ensure we update the target's list with updated dicts
            tgt_data[key] = list(tgt_data_dict.values())
        else:
            # Otherwise, just update the value in the target
            tgt_data[key] = value

    return tgt_data


def main(src_file, tgt_file):
    # Load source JSON data
    with open(src_file) as f:
        src_data = json.load(f)

    # Load target JSON data
    with open(tgt_file) as f:
        tgt_data = json.load(f)

    # Sync properties
    target_data = sync_properties(src_data, tgt_data)

    # Write the updated target data back to the file
    with open(tgt_file, 'w') as f:
        json.dump(target_data, f, indent=2)

    print(f'Successfully synced properties from {src_file} to {tgt_file}')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sync_json.py <src_file> <tgt_file>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])