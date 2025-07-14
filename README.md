# Industrial Automation System with QR Code

## Overview  
This project is an integrated industrial automation system that automatically classifies and sorts products via QR Code scanning. It combines image capture, a robust backend, and Arduino-based physical control to optimize production line workflows.

---

## Academic Information

- **Course:** Computer Engineering  
- **University:** Faculdade Metropolitana de Manaus (FAMETRO)  
- **Duration:** 5 Years (2020 - 2025)

---

## System Architecture

- **Capture and Decoding:**  
  - Camera with OpenCV for QR Code scanning and preprocessing.  
  - Noise filtering and perspective correction for high accuracy.  

- **Backend (FastAPI):**  
  - Asynchronous REST API for data reception, validation, and storage.  
  - Serial communication with Arduino for actuator commands.  
  - SQLite database for persistence and analytics.  
  - Detailed logging for monitoring and debugging.  
  - CORS enabled for frontend integration.

- **Arduino Firmware:**  
  - Servo and conveyor motor control based on backend commands.  
  - JSON message parsing from serial communication.  
  - LCD feedback for real-time system status.  

- **Frontend:**  
  - React Native dashboard for real-time stats and history visualization.  

---

## Key Features

- Real-time QR Code reading and automatic validation.  
- Physical sorting of products by category (e.g., smartphones, tablets).  
- Data persistence with analytics (success rate, average processing time, etc).  
- Robust serial communication with auto-reconnect.  
- Responsive mobile app for monitoring.

---

## Technologies Used

| Component | Technologies / Libraries                   |
| --------- | ----------------------------------------- |
| Backend   | Python, FastAPI, SQLite, PySerial         |
| Capture   | OpenCV, Pyzbar                            |
| Firmware  | Arduino (Servo.h, ArduinoJson, Wire.h)   |
| Frontend  | React Native, Expo                        |
| Logging   | Python logging with configurable levels   |

---

## Quick Setup

### Backend  
1. Install dependencies:  
```bash
pip install fastapi uvicorn pyserial sqlite3 python-multipart
````

2. Set the Arduino serial port (`arduino_port`) in the code.
3. Run the server:

```bash
uvicorn main:app --reload
```

### Arduino

* Upload the firmware via Arduino IDE.

### Frontend

* Follow Expo and React Native setup instructions to run the app.

---

## Repository Structure

```
/backend       # FastAPI backend and SQLite database
/arduino       # Arduino firmware (.ino files)
/frontend      # React Native mobile app
/docs          # Technical documentation and diagrams
```

---

## Notes

* Modular architecture designed for scalability and easy adaptation.
* Optimized serial communication for low latency and reliability.
* Monitoring and logging for proactive maintenance.

---

## Contact

For questions or collaborations, reach out: [arcemateuss@gmail.com](mailto:arcemateuss@gmail.com)

---

Feel free to open issues or contribute! 🚀
