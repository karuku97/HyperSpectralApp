# HyperSpectralApp

Enduser Application for working with Hyper Spectral Cameras. 

## Important properties

- Easy to use for End user
  - [x] Table view of process structure
  - [x] Description for every tool
  - [] Simple Connections for each tool
- Compatibility
  -  [x] APP runs on Windows, Linux and Mac
  - [] Camera Integration


## Status of current Tools:
| Tool name        | Discription                                                                                                                                        | Status     |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|------------|
| load Hyper Cube  | Loads Cube from File (*.BIL) and provides Information from Header file.                                                                            | is working |
| display RGB      | Displays Cube as RGB Picture. Colorchannels can be selected individually.                                                                          | is working |
| extract Spectrum | Point and Area Spectrum can be selected in Picture and added to a List. List can be exported as CSV file. Area Spectrum is calculated via Avarage. |is working|
| capture Cube     | Captures Hyperspectral Image using Basler/Pylon Interface for Prototype Kamera.                                                                     |is working|
