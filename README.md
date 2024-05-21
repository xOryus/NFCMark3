# Proxmark3 to NFC Converter

![Proxmark3 to NFC Converter](https://i.imgur.com/UIeHMss.png)

## Description

Proxmark3 to NFC Converter is a Python application designed to convert JSON dump files exported from Proxmark3 to NFC files compatible with the Flipper Zero. This tool provides an easy-to-use graphical interface for selecting input and output files, and it performs the conversion seamlessly.

## Features

- Converts Proxmark3 JSON dump files to NFC files.
- Supports Mifare Classic card dumps.
- User-friendly graphical interface with Tkinter.
- Logs conversion progress and errors.

## Version Information

- **Version**: 1.0.0


## Installation

### Prerequisites

Ensure you have the following prerequisites installed:

- Python 3.x
- Tkinter


### Installing (soon in .exe)

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/proxmark3-to-nfc-converter.git
    cd proxmark3-to-nfc-converter
    ```

2. Run the application:

    ```bash
    python NFCMark3.py
    ```

## Usage

1. Open the application by running the script:

    ```bash
    python NFCMark3.py
    ```

2. Use the "Browse" button to select the input Proxmark3 JSON dump file.
3. Use the "Browse" button to select the output NFC file location (in files have a example NFC file)
4. Click the "Convert" button to perform the conversion.
5. Check the log area for progress and any error messages.

## Example

Here's an example of the application in use:

![Application Screenshot](https://i.imgur.com/orpzSUa.jpeg)

## Contributing

1. Fork the repository.
2. Create your feature branch:

    ```bash
    git checkout -b feature/AmazingFeature
    ```

3. Commit your changes:

    ```bash
    git commit -m 'Add some AmazingFeature'
    ```

4. Push to the branch:

    ```bash
    git push origin feature/AmazingFeature
    ```

5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, feel free to reach out:

- **Creator**: Strix
- **Discord**: strixmosh

## Acknowledgements

Special thanks to the developers and community of Proxmark3 and Momentum Firmware for their tools and support.
