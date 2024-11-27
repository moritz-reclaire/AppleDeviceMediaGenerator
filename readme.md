# AppleDeviceMediaGenerator

AppleDeviceMediaGenerator is a command line tool designed to generate media assets for presentations. It converts videos such as screen recordings into presentable versions including the border of the selected apple device and includes a transparent background.

Currently supported device frames:
- iPhone 16 Pro
- iPad Pro 11in
- macbook Pro 14in


### Using Binary from Releases

1. Download the latest binary from the [Releases](https://github.com/moritz-reclaire/AppleDeviceMediaGenerator/releases) page.
2. Extract the downloaded file.
3. Open your terminal and navigate to the directory containing the binary.
4. Make executable
    ```
    chmod +x AppleDeviceMediaGenerator
    ```
5. Run:
    ```
    ./AppleDeviceMediaGenerator.py [OPTIONS] INPUT_PATH
    ```

### Building from Source

1. Clone the repository:
    ```
    git clone https://github.com/your-repo/AppleDeviceMediaGenerator.git
    ```
2. Navigate to the project directory:
    ```
    cd AppleDeviceMediaGenerator
    ```
3. Build the project:
    ```
    pyinstaller AppleDeviceMediaGenerator.spec
    ```
4. Run the tool:
    ```
    dist/AppleDeviceMediaGenerator.py [OPTIONS] INPUT_PATH
    ```

## How to Use
Refer to the help page: `AppleDeviceMediaGenerator --help`
```
Usage: AppleDeviceMediaGenerator [OPTIONS] INPUT_PATH

  INPUT_PATH is the path to the raw file e.g. a screen recording or a
  directory.

Options:
  -i, --island                    Adds a dynamic island. Use this if the
                                  screen recording does not include the notch
                                  / dynamic island. Default: --no-island.
  -b, --background                Adds a white background to reduce the file
                                  size. (Currently only supported for iPhone)
  -w, --width INTEGER             The horizontal resolution of the output. Is
                                  ignored when background flag is set.
  --device [iPhone-16-Pro|iPad-11-Pro|macbook-pro-14]
                                  Device used for the frame and aspect ratio.
                                  Default: iPhone-16-Pro.  [required]
  --help                          Show this message and exit.
```

### Examples
Convert file.mp4 using the ipad pro frame.
```
    AppleDeviceMediaGenerator --device=iPad-11-pro file.mp4
```
Convert file.mp4 using the default iPhone 16 pro frame and add the dynamic island.
```
    AppleDeviceMediaGenerator --island file.mp4
```
Convert all files in the current directory using the default iPhone 16 pro frame and slighter higher than default horizontal resolution of 600.
```
    AppleDeviceMediaGenerator -w 600 .
```

## Tips
- Make sure the video you are using roughly matches the aspect-ratio of the target device. Otherwise large areas are cropped to fill the screen while keeping the aspect-ratio.
- For native compatibility with keynote, the output is encoded with Apple ProRes 4444. Keep this in mind, because file sizes can get very big. You can balance file size and quality with the `--width` option or add a background with `-background`.
- When using a prebuilt binary you may have to grant access in system settings
<div style="display: flex; justify-content: center; gap: 1rem; margin-inline: 1rem;">
    <div><img src="readme/alert.png" alt="alert"/> </div>
     <div><img src="readme/grant_access.png" alt="grant access in system settings"/> </div>
</div>