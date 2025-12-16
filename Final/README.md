# 🎰 WhattoDo Box

Group Member: Xinwei Xie(xx374），Xueer Zhang(xz946), Maggie Liang(ml2927)

*A playful interactive decision-making machine*

<img width="1688" height="968" alt="image" src="https://github.com/user-attachments/assets/170a21ef-63e8-4dc2-81f4-63a1fc611fba" />

## 📖 Contents

- [Project Overview](#-project-overview)
- [Big Idea](#-big-idea)
- [Project Timeline](#️-project-timeline)
- [Testing Plan](#-testing-plan)
- [Parts List](#-parts-list)
- [Physical Design Evolution](#-physical-design-evolution)
- [Card Dispensing Mechanism](#️-card-dispensing-mechanism)
- [Hardware Setup](#-hardware-setup)
- [Software Architecture](#-software-architecture)
- [User Testing & Feedback](#-user-testing--feedback)
- [Final Interaction Flow](#-final-interaction-flow)
- [Demo Video](#-demo-video)
- [Reflections](#-reflections)
- [Group Work Distribution](#-group-work-distribution)


## 📌 Project Overview

**WhattoDo Box** is an interactive physical device designed to help users make small life decisions or break out of boredom through a ritualized, fate-like interaction. Users insert a coin, think of a question, make choices through buttons, and receive a randomly dispensed answer card — sometimes good, sometimes bad.

This project combines physical computing, mechanical design, UI on MiiPiTFT, sound & light feedback, and custom card-dispensing mechanisms into one cohesive interactive experience. The documentation is written so that if we woke up with amnesia, we could fully recreate the project from scratch.

## 💡 Big Idea

> *When you don't know what to do — ask the box.*

The WhattoDo Box reacts to a coin insertion and guides users through a step-by-step interaction that ends with a physical card revealing an answer. The randomness of the output creates a sense of **fate**, rather than correctness. The box functions as a hybrid of fortune machine, arcade-style device, motivation box, and piggy bank (coins can be saved inside).

## 🗓️ Project Timeline

| Date | Milestone |
|---|---|
| Nov 15 | Initial prototype: distance sensor & coin detection |
| Nov 22 | Screen (MiiPiTFT) UI integration |
| Nov 28 | Sound & LED system integration |
| Dec 1 | Paper dispensing mechanism |
| Dec 3 | User interaction testing， Final build |
| Dec 8 | Documentation & presentation |

---

## 🧪 Testing Plan

- Test distance sensor accuracy for coin detection  
- Test button response and screen interaction  
- Calibrate servo rotation time for smooth card output  
- Test LED timing and animation patterns  
- Verify correct routing of cards to both exits  
- Observe user understanding and emotional response  

## 🧰 Parts List

### Electronics
- [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/)
- [MiiPiTFT Display](https://www.adafruit.com/product/4393)
- [SparkFun Qwiic GPIO](https://www.sparkfun.com/sparkfun-qwiic-gpio.html)
- [Distance Sensor (SparkFun VL53L1X, Qwiic)](https://www.sparkfun.com/sparkfun-distance-sensor-breakout-4-meter-vl53l1x-qwiic.html)
- [360° Continuous Rotation Servo Motor](https://www.sparkfun.com/servo-generic-high-torque-continuous-rotation-standard-size.html)
- [LEDs ×5 (5V)](https://www.ebay.com/itm/184656453852)
- Bluetooth Speaker

### Fabrication & Materials
- Laser-cut wooden panels  
- 3D-printed card dispenser box  
- Gears (small + large)  
- Rubber bands (for friction)  
- Hot glue

## 🔁 Fall-Back Plan

If the full system failed, we planned several fallback options. First, we could change from dual card dispenser to single card dispenser. If that didn't work, we could replace the card dispenser with a random object dropping machine. As a last option, we could convert the physical system into a screen-only digital version. Each fallback preserves the core idea of randomized decision-making.

## 🧱 Physical Design Evolution

### From Cardboard to Laser-Cut Wood

*[Link to File](https://github.com/m-lmq/Interactive-Lab-Hub/blob/Fall2025/Final/Box.ai)*


The initial prototype was built from cardboard, but the final version uses a laser-cut wooden box. We precisely measured and cut openings for the MiiPiTFT screen, buttons, LEDs, two card exits, and rear cable exit. All components are flush with the surface, creating a clean and integrated appearance. The card exit was upgraded from one slot to two slots.

<div align="center">
  <img src="https://github.com/user-attachments/assets/10d667a1-3713-4755-a6c7-608970ff49b6" width="45%">
  <img src="https://github.com/user-attachments/assets/c4cb1aab-8729-4244-a5b2-bf3798e4af8c" width="45%">
</div>

## ⚙️ Card Dispensing Mechanism

*[Link to File](https://github.com/m-lmq/Interactive-Lab-Hub/blob/Fall2025/Final/card_dispenser.3mf)*

### Original Plan

The original plan used two servo motors where each servo controlled one card exit and drove a roller to push out a single card.

### Final Mechanical Design

To better simulate a realistic automatic card dispenser, we designed and tested a custom 3D-printed card dispensing box. The card slot holds multiple cards stacked vertically with a hollow bottom. Rollers are installed underneath the cards and connect to a small gear, then large gear, then external knob. Rotating the knob spins the rollers and pushes cards outward. This design allows multiple cards per slot instead of one card at a time.

We replaced the manual knob with a 360° continuous servo motor attached directly to the gear. Card output is controlled by setting servo rotation duration, which was calibrated through multiple rounds of testing.

<div align="center">
  <img src="https://github.com/user-attachments/assets/a3c9eee7-facd-4609-8a9e-f2447257fadd" width="45%">
  <img src="https://github.com/user-attachments/assets/2da6dd31-1790-4075-9949-4bfa87a026b6" width="45%">
</div>


### ❗ Major Problem & Solution

The surface of the 3D-printed rollers had too little friction, so cards slipped instead of being pushed out. We tried increasing card weight and adding springs on top of the cards, but these attempts failed. The final working solution was adding friction strips using rubber bands. We cut rubber bands and glued them onto the rollers with hot glue, which significantly increased friction and enabled reliable card output.

<details>
  <summary><strong>▶ Card Dispensing Testing Video </strong></summary>
  <video src="https://github.com/user-attachments/assets/ff2214b8-66dc-4863-9c8b-be157ee2063f" controls></video>
</details>

<div align="center">
  <img src="https://github.com/user-attachments/assets/5a48e806-b9e0-49af-a9c0-e9fdee7918de" width="45%">
  <img src="https://github.com/user-attachments/assets/cc1811ff-d28f-4a77-b45a-8c325ad21dc2" width="45%">
  <br><br>
  <img src="https://github.com/user-attachments/assets/21e21cd3-1174-4a65-946b-aa04fc19af3d" width="45%">
  <img src="https://github.com/user-attachments/assets/32ee8400-8a2e-4cae-8e27-a2906d234cf1" width="45%">
</div>


## 🔌 Hardware Setup

This section documents how all hardware components are connected, from the Raspberry Pi to sensors, LEDs, and actuators. The goal is that the system can be fully rebuilt from scratch using this description alone.


<div align="center">
  <img src="https://github.com/user-attachments/assets/5e95977c-5e9c-4b24-abac-a99802af8301" width="30%">
  <img src="https://github.com/user-attachments/assets/5e95977c-5e9c-4b24-abac-a99802af8301" width="30%">
  <img src="https://github.com/user-attachments/assets/ff5c8fc1-1eab-4f64-a140-088485b68128" width="30%">
  <br><br>
  <img src="https://github.com/user-attachments/assets/c8ebedea-6111-490d-9636-6974ae682506" width="45%">
  <img src="https://github.com/user-attachments/assets/6bc48a03-db70-4c88-9244-d45a43db37ce" width="45%">
</div>

###  Main Board

The Raspberry Pi 5 acts as the central controller for logic, UI, sensing, and actuation. It runs the Python scripts that manage interaction flow, sensor readings, LED animations, servo motor timing, and sound and screen output.

### 🔗 I2C Expansion & GPIO Control

The SparkFun Qwiic GPIO is used to expand GPIO access via the I2C bus. This board simplifies wiring and allows multiple devices (LEDs, sensors) to be chained cleanly using Qwiic cables. It connects to the Raspberry Pi 5 via I2C using a Qwiic cable.

### 💡 LED Output (Visual Feedback)

Five 5V LEDs are used to visualize the waiting state after coin insertion. LEDs light up one by one while the user is thinking, and all turn on simultaneously when a card is dispensed. The LEDs are connected to Qwiic GPIO output pins and controlled through I2C commands from the Raspberry Pi.

### 📏 Distance Sensor (Coin Detection)

The SparkFun Distance Sensor (VL53L1X, Qwiic) detects when a coin passes through the slot. This sensor is critical for triggering the interaction flow. It connects from Qwiic GPIO to the Distance Sensor via Qwiic cable, communicating through I2C. Sensor readings are continuously polled by the Raspberry Pi.

<div align="center">
  <img src="https://github.com/user-attachments/assets/81bc19d4-ab65-45c4-85a5-f12aeedef9d5" width="45%">
  <img src="https://github.com/user-attachments/assets/63c3ff0e-0a84-4731-80b1-93c32517b222" width="45%">
</div>


### ⚙️ Servo Motor (Card Dispensing)

The 360° Continuous Rotation Servo Motor drives the gear-based card dispensing mechanism. The servo rotates for a calibrated duration to push one card out of the slot. The servo signal pin connects to Raspberry Pi GPIO (PWM), servo power connects to external 5V supply with shared ground, and servo timing (rotation duration) is controlled in software.


### 🖥️ Display & User Input

The MiiPiTFT Display is used to display instructions, prompts, and choices to the user. Buttons on the display are used for user input during the interaction flow.

### 🔊 Audio Output

The Bluetooth Speaker provides audio feedback including coin insertion confirmation sound and background mysterious music during waiting states. It pairs wirelessly with the Raspberry Pi via Bluetooth, and audio is triggered through Python scripts.


## 💻 Software Architecture

The system uses Python language. GPIO is used for LEDs and servo motor. MiiPiTFT is used for UI display and buttons. The system follows a state-based interaction flow: Idle → Coin detected → Waiting → Choice → Dispense. All code is archived in this repository.

> 🔗 **Code Archive:** *([Link to Code](https://github.com/m-lmq/Interactive-Lab-Hub/blob/Fall2025/Final/1201.py))*

## 👥 User Testing & Feedback

We conducted informal user testing with classmates and instructors during the development process.

### Display & Atmosphere
In early versions, the on-screen instructions were very explicit and direct. After our instructor tried the prototype, they suggested that the interaction could benefit from a more **mysterious and abstract tone**, making the experience feel less instructional and more like a **random fate or destiny machine**. Based on this feedback, we adjusted the wording and timing of the display to feel more virtual and less deterministic.

### Screen Size
Some users noted that the screen felt relatively small, especially during option selection. While we agreed that a larger display could improve readability, this limitation could not be addressed due to **budget and hardware constraints**. Instead, we focused on simplifying on-screen text and relying more on lights and sound to communicate system state.

### Light Feedback
Several users responded very positively to the LED behavior. In particular, they liked how the lights flashed in different patterns depending on the system state. The **one-by-one LED animation during the waiting phase** was frequently mentioned as engaging, as it clearly communicated that the system was thinking or waiting, and helped build anticipation before the card was dispensed.

Overall, user feedback helped us refine the balance between clarity and mystery, reinforcing the experience of chance rather than control.

## 🧩 Final Interaction Flow

In the idle state, the MiiPiTFT displays "Insert coin". When the user inserts a coin, the distance sensor detects it, an immediate sound effect confirms success, and mysterious background music starts playing. Five LEDs then light up one by one in sequence, indicating the system is waiting for user input.

The screen displays "Hold one question in your mind..." and the user presses the button corresponding to "← Yes, I'm ready." Next, two options appear on screen: Option 1 for random card output, or Option 2 to go to a precise choice page.

For Option 1, the system randomly chooses one of two card exits. For Option 2, a next screen appears with Choice A leading to Exit 1 and Choice B leading to Exit 2. Finally, the card is dispensed, all LEDs turn on simultaneously, and the card contains an answer to the user's question (positive, negative, or ambiguous).

<details>
  <summary><strong>▶ Testing Video without Box</strong></summary>
  <video src="https://github.com/user-attachments/assets/49b30265-b461-470c-b232-cfcf7ec4eeb7" controls></video>
</details>

<details>
  <summary><strong>▶ Testing Video with Box</strong></summary>
  <video src="https://github.com/user-attachments/assets/5735d8a8-f5b6-434b-a8f5-3b81f2f96412" controls></video>
</details>

## 🎥 Demo Video

A demo video shows the full user interaction, coin insertion, UI flow, LED animation, and card dispensing from both exits.

> 🎬 **Video Link:**

https://github.com/user-attachments/assets/6b0d8050-0e30-4d08-94c9-2cafd0cb4c8f

https://github.com/user-attachments/assets/6383ccdf-b10e-4845-afb9-9b6c95effeb8

## 🪞 Reflections

### What We Learned
We learned that mechanical friction is as important as code. Synchronization between sound, light, and motion defines user experience. Physical randomness feels more meaningful than digital randomness.

### What We Wish We Knew Earlier
We wish we knew earlier that 3D printing material properties are unpredictable, continuous servo motors require extensive calibration, and precise enclosure design saves significant debugging time later.

## 👥 Group Work Distribution

**Team Members:** Maggie Liang (ml2927), Xueer Zhang (xz946), Xinwei Xie (xx2185)

### Roles & Responsibilities

Xinwei Xie (xx2185) was primarily responsible for coding and electronics integration, including overall system logic and interaction flow, servo motor control and card dispensing logic, distance sensor integration, music playback and sound timing, and MiiPiTFT UI logic and button mapping. Maggie Liang assisted with debugging and testing during this process.

Xueer Zhang (xz946) was primarily responsible for the mechanical and physical design, including card dispenser box design and testing, structural design of the main enclosure, and iteration and debugging of the dispensing mechanism. Xueer also handled the final aesthetic finishing of the box, refining its visual appearance.

Maggie Liang (ml2927) was primarily responsible for card dispenser box and enclosure design (working closely with Xueer Zhang), mechanical testing and iteration, assisting with electronics setup and system debugging, and supporting interaction flow refinement and documentation.

All members collaborated throughout testing, iteration, and final integration to ensure the system functioned as a cohesive interactive experience.

## 🌟 Final Note

The WhattoDo Box evolved from a simple sensor-based prototype into a cohesive interactive object that blends physical ritual, randomness, and reflection. If we woke up tomorrow with amnesia, this README would allow us to build it again.
