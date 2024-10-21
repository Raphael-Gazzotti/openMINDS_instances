import json
import sys


def sync_properties(src_data, tgt_data):
    """Sync properties from src_data to tgt_data, skipping specified keys."""
    for key, value in src_data.items():
        # Skip special keys that should not be modified
        if key in ["@vocab", "@type", "@id"]:
            continue
        
        # If the value is a dictionary, recurse
        if isinstance(value, dict):
            tgt_data[key] = tgt_data.get(key, {})
            tgt_data[key] = sync_properties(value, tgt_data[key])
        elif isinstance(value, list):
            tgt_data[key] = tgt_data.get(key, [])
            
            # If the list contains dicts with '@id', handle them specifically
            if all(isinstance(item, dict) and '@id' in item for item in value):
                tgt_data_dict = {item['@id']: item for item in tgt_data[key] if isinstance(item, dict) and '@id' in item}
                
                for item in value:
                    if isinstance(item, dict) and '@id' in item:
                        # Update existing items but skip special keys
                        if item['@id'] in tgt_data_dict:
                            tgt_data_dict[item['@id']] = sync_properties(item, tgt_data_dict[item['@id']])
                    else:
                        # Append non-dict items directly
                        tgt_data[key].append(item)

                tgt_data[key] = list(tgt_data_dict.values())
            else:
                # Update existing items in the list if they exist
                for item in value:
                    if isinstance(item, dict) and '@type' in item:
                        # Find existing item in target list by type or other identifier
                        for tgt_item in tgt_data[key]:
                            if isinstance(tgt_item, dict) and tgt_item.get('@type') == item['@type']:
                                # Update existing item with the values from source
                                tgt_item.update(item)  # Only update values, not keys like @type
                                break
                    else:
                        # Append non-dict items directly
                        tgt_data[key].append(item) 
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
