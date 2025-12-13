# 🎰 WhattoDo Box  
*A playful interactive decision-making machine*

---

## 📌 Project Overview

**WhattoDo Box** is an interactive physical device designed to help users make small life decisions or break out of boredom through a ritualized, fate-like interaction.

Users insert a coin, think of a question, make choices through buttons, and receive a randomly dispensed answer card — sometimes good, sometimes bad — reinforcing a sense of chance, destiny, and play.

This project combines **physical computing**, **mechanical design**, **UI on MiiPiTFT**, **sound & light feedback**, and **custom card-dispensing mechanisms** into one cohesive interactive experience.

The documentation is written so that **if we woke up with amnesia**, we could fully recreate the project from scratch.

---

## 🧠 Big Idea

> *When you don’t know what to do — ask the box.*

The WhattoDo Box reacts to a coin insertion and guides users through a step-by-step interaction that ends with a physical card revealing an answer.  
The randomness of the output creates a sense of **fate**, rather than correctness.

The box functions as a hybrid of:
- Fortune machine  
- Arcade-style device  
- Motivation box  
- Piggy bank (coins can be saved inside)

---

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

## 🧩 Final Interaction Flow

1. **Idle State**  
   - MiiPiTFT displays:  
     `Insert coin`

2. **Coin Detection**  
   - User inserts a coin  
   - Distance sensor detects the coin  
   - Immediate sound effect confirms success  
   - A mysterious background music starts playing

3. **Waiting Animation**  
   - Five LEDs light up **one by one** in sequence  
   - Indicates the system is waiting for user input

4. **User Prompt**  
   - Screen displays:  
     `Hold one question in your mind...`  
   - User presses the button corresponding to  
     `← Yes, I'm ready.`

5. **Decision Screen**  
   - Two options appear on screen:
     - Option 1: Random card output  
     - Option 2: Go to a precise choice page

6. **Card Dispensing Logic**  
   - **Option 1:**  
     - Randomly chooses one of two card exits  
   - **Option 2:**  
     - Next screen appears  
       - Choice A → Exit 1  
       - Choice B → Exit 2  

7. **Final Output**  
   - Card is dispensed  
   - All LEDs turn on simultaneously  
   - The card contains an answer to the user’s question  
     (positive / negative / ambiguous)

---

## 🧱 Physical Design Evolution

### From Cardboard to Laser-Cut Wood

- Initial prototype built from **cardboard**
- Final version uses a **laser-cut wooden box**
- Precisely measured and cut openings for:
  - MiiPiTFT screen  
  - Buttons  
  - LEDs  
  - Two card exits  
  - Rear cable exit  

All components are flush with the surface, creating a clean and integrated appearance.  
The card exit was upgraded from **one slot to two slots**.
<div align="center">
  <img src="https://github.com/user-attachments/assets/10d667a1-3713-4755-a6c7-608970ff49b6" width="45%">
  <img src="https://github.com/user-attachments/assets/c4cb1aab-8729-4244-a5b2-bf3798e4af8c" width="45%">
</div>



---

## ⚙️ Card Dispensing Mechanism (Detailed)

### Original Plan

- Two servo motors  
- Each servo controlled one card exit  
- Each servo drove a roller to push out a single card  

### Final Mechanical Design (Implemented)

To better simulate a realistic automatic card dispenser, we designed and tested a **custom 3D-printed card dispensing box**.

#### Mechanical Structure

- Card slot holds multiple cards stacked vertically  
- Bottom of the slot is hollow  
- Rollers are installed underneath the cards  
- Rollers connect to:
  - Small gear → large gear → external knob  
- Rotating the knob spins the rollers and pushes cards outward  

This design allows **multiple cards per slot**, instead of one card at a time.

#### Motorization

- Replaced the manual knob with a **360° continuous servo motor**
- Servo is attached directly to the gear
- Card output is controlled by setting **servo rotation duration**
- Multiple rounds of testing were used to calibrate timing

---

### ❗ Major Problem & Solution

**Problem:**  
The surface of the 3D-printed rollers had **too little friction**, so cards slipped instead of being pushed out.

**Attempts that failed:**
- Increasing card weight  
- Adding springs on top of the cards  

**Final Working Solution:**  
- Added friction strips using **rubber bands**
- Rubber bands were cut and glued onto the rollers with hot glue
- This significantly increased friction and enabled reliable card output

This solution was used in the final version.

![0d538c4ac191750f55c692853734529](https://github.com/user-attachments/assets/2da6dd31-1790-4075-9949-4bfa87a026b6)
<div align="center">
  <img src="https://github.com/user-attachments/assets/f12d8245-fef0-41b1-8ded-99278d43246a" width="30%">
  <img src="https://github.com/user-attachments/assets/5a48e806-b9e0-49af-a9c0-e9fdee7918de" width="30%">
  <img src="https://github.com/user-attachments/assets/cc1811ff-d28f-4a77-b45a-8c325ad21dc2" width="30%">
</div>

<details>
  <summary><strong>▶ Card Dispensing Testing Video without Box</strong></summary>
  <video src="https://github.com/user-attachments/assets/49b30265-b461-470c-b232-cfcf7ec4eeb7" controls></video>
</details>

<details>
  <summary><strong>▶ Card Dispensing Testing Video with Box</strong></summary>
  <video src="https://github.com/user-attachments/assets/5735d8a8-f5b6-434b-a8f5-3b81f2f96412" controls></video>
</details>





---

## 🧪 Testing Plan

- Test distance sensor accuracy for coin detection  
- Test button response and screen interaction  
- Calibrate servo rotation time for smooth card output  
- Test LED timing and animation patterns  
- Verify correct routing of cards to both exits  
- Observe user understanding and emotional response  

---

## 🧰 Parts List

### Electronics
- Raspberry Pi 5  
- Distance sensor  
- 360° servo motor  
- MiiPiTFT display  
- LEDs ×5  
- Speaker  

### Fabrication & Materials
- Laser-cut wooden panels  
- 3D-printed card dispenser box  
- Gears (small + large)  
- Rubber bands (for friction)  
- Hot glue  

---

## 💻 Software Architecture

- Language: Python  
- GPIO used for:
  - LEDs  
  - Servo motor  
- MiiPiTFT used for UI display and Buttons
- State-based interaction flow:
  - Idle → Coin detected → Waiting → Choice → Dispense  

All code is archived in this repository.

> 🔗 **Code Archive:** *(insert GitHub link here)*

---

## 🎥 Demo Video

A demo video shows:
- Full user interaction
- Coin insertion
- UI flow
- LED animation
- Card dispensing from both exits

> 🎬 **Video Link:** *(insert link here)*

---

## 🔁 Fall-Back Plan

If the full system failed, we planned the following fallback options:

1. Dual card dispenser → Single card dispenser  
2. Card dispenser → Random object dropping machine  
3. Physical system → Screen-only digital version  

Each fallback preserves the core idea of **randomized decision-making**.

---

## 🪞 Reflections

### What We Learned
- Mechanical friction is as important as code
- Synchronization between sound, light, and motion defines user experience
- Physical randomness feels more meaningful than digital randomness

### What We Wish We Knew Earlier
- 3D printing material properties are unpredictable
- Continuous servo motors require extensive calibration
- Precise enclosure design saves significant debugging time later

---

## 👥 Group Work Distribution

**Team Members**
- Maggie Liang (ml2927)  
- Xueer Zhang (xz946)  
- Xinwei Xie (xx2185)

### Roles & Responsibilities

- **Xinwei Xie (xx2185)**  
  Primarily responsible for **coding and electronics integration**, including:
  - Overall system logic and interaction flow  
  - Servo motor control and card dispensing logic  
  - Distance sensor integration  
  - Music playback and sound timing  
  - MiiPiTFT UI logic and button mapping  
  Maggie Liang assisted with debugging and testing during this process.

- **Xueer Zhang (xz946)**  
  Primarily responsible for the **mechanical and physical design**, including:
  - Card dispenser box design and testing  
  - Structural design of the main enclosure  
  - Iteration and debugging of the dispensing mechanism  
  Xueer also handled the **final aesthetic finishing** of the box, refining its visual appearance.

- **Maggie Liang (ml2927)**  
  Primarily responsible for:
  - Card dispenser box and enclosure design (working closely with Xueer Zhang)  
  - Mechanical testing and iteration  
  - Assisting with electronics setup and system debugging  
  - Supporting interaction flow refinement and documentation  

All members collaborated throughout testing, iteration, and final integration to ensure the system functioned as a cohesive interactive experience.

---

## 🌟 Final Note

The WhattoDo Box evolved from a simple sensor-based prototype into a cohesive interactive object that blends physical ritual, randomness, and reflection.

If we woke up tomorrow with amnesia, this README would allow us to build it again.
