# Staging Interaction
# Tinkerbell Light: Smart Pet Mood Lamp

## Name: Maggie Liang(ml2927) Xueer Zhang(xz946) Xinwei Xie(xx2185)

## Part A. Plan

### Topic
Our design for the "Tinkerbell Light" is a smart pet lamp. The lamp features an LED light and sensors that monitor the pet's activity and heart rate, changing the light color according to the pet’s mood.

### Setting
The interaction takes place in the living room in the evening, with the owner present.

### Players
- Pet Dog
- Pet Owner  
- The Pet Mood Lamp (the “Tinkerbell light”)

### Activity
- The pet is in different states (calm, restless, asleep).
- The sensor light responds with lighting changes:
  - Blue → Rest
  - Green → Normal  
  - Yellow → Exciting
  - Red → Anxiety
- The owner interprets the lamp’s colors and decides how to react (e.g., feed, play, or leave the pet to rest).

### Goals
- The pet wants to express needs (comfort, food, attention).
- The owner wants to understand the pet without guesswork.
- The lamp acts as a “translator” between them using only light.

### Storyboard
![Storyboard](./storyboard.png)

### Feedback Summary
We received feedback from another group suggesting we clarify how the pet's mood is monitored. After research, we found that similar to how an Apple Watch monitors blood pressure and heart rate, we can implement a collar for the pet to wear to track these metrics.


## Part B. Act Out the Interaction

We physically acted out the planned interaction, pretending the device performed the scripted functions.

### Did anything seem better on paper than when acted out?
Yes. On paper, mapping the dog’s emotional states directly to light colors (e.g., red = anxious, blue = calm) seemed straightforward. However, during the acted-out scenario, we realized the dog’s behavior is unpredictable and cannot be perfectly controlled to match the storyboard.

### Did new ideas emerge during the acting?
We discovered that adding auditory alerts could further help remind the owner about the pet’s current state.



## Part C. Prototype the Device

We used a smartphone as a stand-in for the device, with its browser acting as a “light” and a remote control interface to change the light color.

### Feedback on the Tinkerbelle Tool
We successfully built the system and set up remote control. One piece of feedback is that Tinkerbelle does not support entering color codes directly, which makes re-selecting the same color on the palette difficult unless using the default provided colors.


## Part D. Wizard the Device

We set up a wizarding system allowing remote control of the device while one team member acted with it. Zoom was used to record videos, and we pinned the relevant video feed to capture the scene.


### Setup the Device
*[Setup the Device](https://www.youtube.com/watch?v=D4cC2wBMVeg)*

### First Recording Attempts
*[First Attempt](https://www.youtube.com/shorts/a3TpJAGhahQ)*

We used the device to interact with a cat, using two color signals: blue for "rest" and yellow for "feeding."

### Updated Interaction After Paper Prototyping
![Photo for dog](./photo-for-dog.png)

See Section F for the video.

After refining the storyboard, we applied the interaction to a dog with 4 colors.
- The sensor light responds with lighting changes:
  - Blue → Rest
  - Green → Normal  
  - Yellow → Exciting
  - Red → Anxiety



## Part E. Costume the Device

We developed three conceptual costumes to use the phone as the device, considering the environment and usability.

### Sketches
*![Costume 1](costume.png)
![Costume 2&3](./costume-device.png)*

### Design Considerations
- **Dog’s comfort**: Lights should be soft, not harsh or strobing, to avoid frightening or stressing the dog.
- **Light transitions**: Should be gradual (fade-in/fade-out) for a calming effect.
- **Environmental factors**: The device should be safe from overheating and water exposure, especially in a living room setting.
- **Visibility**: Colors should be bright enough to be noticeable but not overwhelming.



## Part F. Record

### [Updated Interaction After Paper Prototyping](https://youtu.be/2MFH3JHRcug)

# Staging Interaction, Part 2
# Smart Hydration Coaster

## Project Overview

This project presents an interactive hydration reminder device designed to help users maintain healthy drinking habits through gentle visual cues and progressive feedback mechanisms.

## Partner Feedback Summary

We received valuable feedback from our assigned partners who reviewed our initial video prototype. They provided insights about the scene interpretation and character goals, helping us refine our approach to user interaction design. Their observations about the clarity of our demonstration guided our improvements for the second iteration.

## Design Concept

Our smart hydration coaster represents a creative approach to addressing the common problem of forgetting to drink water during busy work periods or encouraging children to maintain proper hydration habits.

### Setting and Context

The interaction takes place primarily in office environments during afternoon work sessions, when users are deeply focused and often forget basic self-care needs like drinking water. A secondary setting includes home dining tables or play areas where children need gentle encouragement to develop healthy hydration habits.

The device is designed to function seamlessly in both professional and domestic environments, adapting its behavior to suit different user needs and social contexts.

### Target Users

**Primary Users:**
- Office workers and students who forget to drink water during focused work
- Children who need encouragement to maintain regular hydration

**Secondary Users:**
- Coworkers/roommates (indirect observers)
- Parents/caregivers (supervisory role for children)

### Interaction Flow

1. User places water cup on the smart coaster
2. 45-minute hydration cycle begins with time-based visual feedback:
   - **45-21 minutes**: Soft green glow (normal state)
   - **20-6 minutes**: Gradual yellow breathing light (gentle reminder)
   - **5-2 minutes**: Solid red light (urgent reminder)
   - **Final minute**: Flashing red light with "beep beep beep" sound
3. If no drinking is detected after 45 minutes, coaster tilts to encourage action
4. Timer resets when user drinks and replaces the cup

### Design Goals

The primary objective is helping users maintain consistent hydration without requiring conscious effort or disrupting their workflow. The device aims to build sustainable habits through positive reinforcement rather than punishment-based mechanisms.

For families with children, the coaster serves as an engaging tool that makes drinking water more interactive and fun. Parents and caregivers can use the device to establish routine hydration habits in a supportive, non-confrontational manner.

Office environments benefit from the device's subtle operation, which provides personal reminders without creating distractions for colleagues or disrupting professional atmospheres.

## Storyboard and Planning

Our initial planning phase involved detailed storyboarding to visualize the user experience across different scenarios and time periods. The storyboards helped us understand potential pain points and opportunities for improvement before moving to physical prototyping.

## Feedback and Iteration

Initial feedback praised the intuitive light progression system and the combination of gentle reminders with firm consequences. Reviewers appreciated the clear visual language of the green-yellow-red transition pattern, finding it immediately understandable across different user groups.

However, concerns were raised about the original flipping mechanism, particularly regarding mess creation in office settings and safety issues with hot beverages. This feedback led us to reconsider the consequence system and explore alternative approaches.

## Physical Prototyping Insights

Acting out the planned interactions revealed significant practical challenges with our initial design. The water-spilling feature, while theoretically motivating, proved impractical when demonstrated in realistic settings with laptops, documents, and other sensitive materials nearby.

Safety concerns became apparent when considering hot beverages like tea or coffee, which could cause burns if spilled through the mechanical flipping action. These realizations prompted us to develop alternative consequence mechanisms.

Through physical testing, we developed the concept of a magnetic attachment system between the cup and coaster, allowing for controlled tilting motions instead of complete spilling. This approach maintains the physical feedback element while eliminating safety and mess concerns.

## Technical Implementation

We utilized the Tinkerbelle tool for prototyping the lighting system, using smartphones as stand-in devices controlled through a browser-based interface. This approach allowed us to test color transitions and timing sequences effectively.

The Tinkerbelle system performed well overall, though we noted limitations in color code input functionality that required workarounds during testing. The remote control capabilities enabled realistic simulation of the automated timing sequences.

## Device Appearance and Considerations

The coaster's visual design prioritizes functionality while addressing environmental challenges. Water resistance is essential given the device's proximity to beverages, requiring durable, waterproof materials that can withstand daily use and cleaning.

Heat resistance capabilities ensure the device can safely accommodate hot drinks without material degradation or user safety risks. The lighting system uses bright enough LEDs to clearly communicate status changes while remaining comfortable for extended viewing.

Customization options allow users to select appropriate alert methods for their environment, such as light-only modes for quiet office settings or combined audio-visual alerts for home use. The tilting mechanism for children adds a playful element that maintains engagement without creating serious consequences.

We envision future integration with mobile applications that could provide additional customization options, usage tracking, and personalized hydration goals based on individual needs and preferences.

