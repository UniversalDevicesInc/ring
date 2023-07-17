
# Ring Node Server (c) 2023 Universal Devices

The Ring Node Server retrieves your Ring devices and allows you to 
get motion and ring events, and also control floodlights.

## Installation
The settings for this node are:

### Short Poll
   - The interval used to poll the battery level
### Long Poll
   - The interval used to resubscribe to Ring events

### Custom params
   - shared
     - Set to "true" to include shared devices
     - You will need to re-run device discovery after

## Requirements

1. PG3x (eisy, or Polisy updated with PG3x)
2. ISY firmware 5.6.0 or later
3. PG3 Remote connection must be enabled and active
    - Settings are in Portal under Select Tools | Maintenance | PG3 Remote connection

# Release Notes

- 1.1.3 07/17/2023
  - When updating properties, always send them to IoX. This is to prevent blank properties.
- 1.1.2 07/05/2023
  - Enhanced error handling when nodeserver is not yet linked to a Ring account
- 1.1.1 05/23/2023
  - Fixed logging
- 1.1.0 05/16/2023
  - Added support for shared devices
- 1.0.5 05/15/2023
  - Fixed bug with ownership verification when using shared devices
- 1.0.4 04/18/2023
  - Initial working beta version published to github
