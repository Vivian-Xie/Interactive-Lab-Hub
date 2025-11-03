# Observant Systems

**NAMES OF COLLABORATORS HERE** Maggie Liang(ml2927) Xueer Zhang(xz946) Xinwei Xie(xx2185)


For lab this week, we focus on creating interactive systems that can detect and respond to events or stimuli in the environment of the Pi, like the Boat Detector we mentioned in lecture. 
Your **observant device** could, for example, count items, find objects, recognize an event or continuously monitor a room.

This lab will help you think through the design of observant systems, particularly corner cases that the algorithms need to be aware of.

## Prep

1.  Install VNC on your laptop if you have not yet done so. This lab will actually require you to run script on your Pi through VNC so that you can see the video stream. Please refer to the [prep for Lab 2](https://github.com/FAR-Lab/Interactive-Lab-Hub/blob/-/Lab%202/prep.md#using-vnc-to-see-your-pi-desktop).
2.  Install the dependencies as described in the [prep document](prep.md). 
3.  Read about [OpenCV](https://opencv.org/about/),[Pytorch](https://pytorch.org/), [MediaPipe](https://mediapipe.dev/), and [TeachableMachines](https://teachablemachine.withgoogle.com/).
4.  Read Belloti, et al.'s [Making Sense of Sensing Systems: Five Questions for Designers and Researchers](https://www.cc.gatech.edu/~keith/pubs/chi2002-sensing.pdf).

### For the lab, you will need:
1. Pull the new Github Repo
1. Raspberry Pi
1. Webcam 

### Deliverables for this lab are:
1. Show pictures, videos of the "sense-making" algorithms you tried.
1. Show a video of how you embed one of these algorithms into your observant system.
1. Test, characterize your interactive device. Show faults in the detection and how the system handled it.

## Overview
Building upon the paper-airplane metaphor (we're understanding the material of machine learning for design), here are the four sections of the lab activity:

A) [Play](#part-a)

B) [Fold](#part-b)

C) [Flight test](#part-c)

D) [Reflect](#part-d)

---

### Part A
### Play with different sense-making algorithms.

<details>
<summary><h4><strong>Pytorch for object recognition</strong></h4></summary>

For this first demo, you will be using PyTorch and running a MobileNet v2 classification model in real time (30 fps+) on the CPU. We will be following steps adapted from [this tutorial](https://pytorch.org/tutorials/intermediate/realtime_rpi.html).

![torch](Readme_files/pyt.gif)


To get started, install dependencies into a virtual environment for this exercise as described in [prep.md](prep.md).

Make sure your webcam is connected.

You can check the installation by running:

```
python -c "import torch; print(torch.__version__)"
```

If everything is ok, you should be able to start doing object recognition. For this default example, we use [MobileNet_v2](https://arxiv.org/abs/1801.04381). This model is able to perform object recognition for 1000 object classes (check [classes.json](classes.json) to see which ones.

Start detection by running  

```
python infer.py
```

The first 2 inferences will be slower. Now, you can try placing several objects in front of the camera.

Read the `infer.py` script and become familiar with the code. You can change the video resolution and frames per second (FPS). You may also use the weights of the larger pre-trained mobilenet_v3_large model, as described [here](https://pytorch.org/tutorials/intermediate/realtime_rpi.html#model-choices).

#### More classes

[PyTorch supports transfer learning](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html), so you can fine‑tune and transfer learn models to recognize your own objects. It requires extra steps, so we won't cover it here.

For more details on transfer learning and deployment to embedded devices, see Deep Learning on Embedded Systems: A Hands‑On Approach Using Jetson Nano and Raspberry Pi (Tariq M. Arif). [Chapter 10](https://onlinelibrary.wiley.com/doi/10.1002/9781394269297.ch10) covers transfer learning for object detection on desktop, and [Chapter 15](https://onlinelibrary.wiley.com/doi/10.1002/9781394269297.ch15) describes moving models to the Pi using ONNX.

### Machine Vision With Other Tools
The following sections describe tools ([MediaPipe](#mediapipe) and [Teachable Machines](#teachable-machines)).

</details>

https://github.com/user-attachments/assets/91717ab8-b622-45bc-8059-351f32000585

https://github.com/user-attachments/assets/ea6a155e-8355-434b-b43d-6fafae67bb72


<details>
<summary><h4><strong>MediaPipe</strong></h4></summary>

A established open source and efficient method of extracting information from video streams comes out of Google's [MediaPipe](https://mediapipe.dev/), which offers state of the art face, face mesh, hand pose, and body pose detection.

![Media pipe](Readme_files/mp.gif)

To get started, install dependencies into a virtual environment for this exercise as described in [prep.md](prep.md):

Each of the installs will take a while, please be patient. After successfully installing mediapipe, connect your webcam to your Pi and use **VNC to access to your Pi**, open the terminal, and go to Lab 5 folder and run the hand pose detection script we provide:
(***it will not work if you use ssh from your laptop***)


```
(venv-ml) pi@ixe00:~ $ cd Interactive-Lab-Hub/Lab\ 5
(venv-ml) pi@ixe00:~ Interactive-Lab-Hub/Lab 5 $ python hand_pose.py
```

Try the two main features of this script: 1) pinching for percentage control, and 2) "[Quiet Coyote](https://www.youtube.com/watch?v=qsKlNVpY7zg)" for instant percentage setting. Notice how this example uses hardcoded positions and relates those positions with a desired set of events, in `hand_pose.py`. 

Consider how you might use this position based approach to create an interaction, and write how you might use it on either face, hand or body pose tracking.

(You might also consider how this notion of percentage control with hand tracking might be used in some of the physical UI you may have experimented with in the last lab, for instance in controlling a servo or rotary encoder.)
</details>

https://github.com/user-attachments/assets/8b46ae82-065d-4bf8-9f28-90cad102fe9a

https://github.com/user-attachments/assets/fdd56732-d369-4d55-8e5d-6a4ea8678aee

https://github.com/user-attachments/assets/47ea991b-1f54-4a0c-bcb3-29f378120505


<details>
<summary><h4><strong>Moondream Vision-Language Model</strong></h4></summary>

[Moondream](https://www.ollama.com/library/moondream) is a lightweight vision-language model that can understand and answer questions about images. Unlike the classification models above, Moondream can describe images in natural language and answer specific questions about what it sees.

To use Moondream, first make sure Ollama is running and pull the model:
```bash
ollama pull moondream
```

Then run the simple demo script:
```bash
python moondream_simple.py
```

This will capture an image from your webcam and let you ask questions about it in natural language. Note that vision-language models are slower than classification models (responses may take up to minutes on a Raspberry Pi). There are newer models like [LFM2-VL](https://huggingface.co/LiquidAI/LFM2-VL-450M-GGUF), but many are very recent and not yet optimized for embedded devices.

**Design consideration**: Think about how slower response times change your interaction design. What kinds of observant systems benefit from thoughtful, delayed responses rather than real-time classification? Consider systems that monitor over longer time periods or provide periodic summaries rather than instant feedback.
</details>

![9a3864e46723ebcbf1eb666504bc1ae](https://github.com/user-attachments/assets/fc3894fb-4a4d-42cd-abca-8c95d40008b8)

<details>
<summary><h4><strong>Teachable Machines</strong></h4></summary>
  
Google's [TeachableMachines](https://teachablemachine.withgoogle.com/train) is very useful for prototyping with the capabilities of machine learning. We are using [a python package](https://github.com/MeqdadDev/teachable-machine-lite) with tensorflow lite to simplify the deployment process.

![Tachable Machines Pi](Readme_files/tml_pi.gif)

To get started, install dependencies into a virtual environment for this exercise as described in [prep.md](prep.md):

After installation, connect your webcam to your Pi and use **VNC to access to your Pi**, open the terminal, and go to Lab 5 folder and run the example script:
(***it will not work if you use ssh from your laptop***)


```
(venv-tml) pi@ixe00:~ Interactive-Lab-Hub/Lab 5 $ python tml_example.py
```


Next train your own model. Visit [TeachableMachines](https://teachablemachine.withgoogle.com/train), select Image Project and Standard model. The raspberry pi 4 is capable to run not just the low resource models. Second, use the webcam on your computer to train a model. *Note: It might be advisable to use the pi webcam in a similar setting you want to deploy it to improve performance.*  For each class try to have over 150 samples, and consider adding a background or default class where you have nothing in view so the model is trained to know that this is the background. Then create classes based on what you want the model to classify. Lastly, preview and iterate. Finally export your model as a 'Tensorflow lite' model. You will find an '.tflite' file and a 'labels.txt' file. Upload these to your pi (through one of the many ways such as [scp](https://www.raspberrypi.com/documentation/computers/remote-access.html#using-secure-copy), sftp, [vnc](https://help.realvnc.com/hc/en-us/articles/360002249917-VNC-Connect-and-Raspberry-Pi#transferring-files-to-and-from-your-raspberry-pi-0-6), or a connected visual studio code remote explorer).
![Teachable Machines Browser](Readme_files/tml_browser.gif)
![Tensorflow Lite Download](Readme_files/tml_download-model.png)

Include screenshots of your use of Teachable Machines, and write how you might use this to create your own classifier. Include what different affordances this method brings, compared to the OpenCV or MediaPipe options.

#### (Optional) Legacy audio and computer vision observation approaches
In an earlier version of this class students experimented with observing through audio cues. Find the material here:
[Audio_optional/audio.md](Audio_optional/audio.md). 
Teachable machines provides an audio classifier too. If you want to use audio classification this is our suggested method. 

In an earlier version of this class students experimented with foundational computer vision techniques such as face and flow detection. Techniques like these can be sufficient, more performant, and allow non discrete classification. Find the material here:
[CV_optional/cv.md](CV_optional/cv.md).
</details>

<img width="1704" height="1426" alt="94114f28a8d208a91e101132d9da04d" src="https://github.com/user-attachments/assets/add35c36-2fdf-4c10-9e92-094f4bc4341d" />

<img width="1682" height="1422" alt="83e437c11cf3a882b320e3f4b73fd23" src="https://github.com/user-attachments/assets/bb6fb6d2-7609-4df3-a5b9-7d6350d27e1d" />

https://github.com/user-attachments/assets/c79fd5ee-89c3-481a-a3fb-50a81c84bd38

https://github.com/user-attachments/assets/f738588f-7067-447e-aa5b-9a9616a21c4f


### Part B

### Construct a simple interaction.

#### Model Used
We selected a **Teachable Machine Image Classification model** trained to recognize five everyday activities we want to track:

- **Pen** → studying/writing  
- **Orange** → eating
- **Vitamin** → taking supplements  
- **Cup** → drinking water
- **Book** → reading
- **Raspberry Pi** → doing interactive design work

We trained each class with multiple images captured from different angles and distances. We also varied lighting conditions to improve generalization.

#### Interaction Description

- **Input:** Live video feed from Raspberry Pi camera.
- **Recognition:** The model runs inference continuously.
- **Decision Logic (Temporal Smoothing):**
  - If one label maintains **≥ 0.80 confidence for ~1.5 seconds**, we consider the activity “detected”.
  - If confidence drops below **0.60 for ~0.8 seconds**, we consider the activity “finished”.
- **Output / Feedback:**
  - The screen displays the current detected activity and confidence level.
  - The system logs the activity into a `.csv` sheet:  
    `timestamp, activity, confidence, duration`.

This creates an **automatic habit tracking system** where holding or using an object triggers a log entry without manual input.

---

### Part C
### Test the interaction prototype

Now flight test your interactive prototype and **note down your observations**:

#### When the System Worked Well
- **Pen**: Writing at a desk was recognized reliably (clear shape + movement).
- **Book**: Reading position and rectangular shape produced high confidence.
- **Vitamin**: When the supplement bottle was held close to the camera, detection was consistent.

#### When the System Failed
- **Orange** sometimes failed:  
  It was recognized during training but failed in real usage.  
  Likely causes:
  - Background colors (wood desk / skin tones) visually resemble the orange.
  - Lighting changed between training and testing environments.
- **Cup** (black cup) often misclassified:  
  Any **dark/black object** was sometimes recognized as the cup because the model over-learned **color** rather than **shape**.

#### Why These Failures Occur
- Model relied heavily on **color cues**, not object contour.
- Background and lighting during training were less diverse than in real use.
- Without negative examples of “confusing similar objects,” the model generalizes poorly.

#### Potential Problem Scenarios
- Using the system in a different room or lighting environment.
- Introducing new black objects near the cup (mouse, phone case).
- Eating other orange-colored foods (carrots, snacks) may trigger false detections.

#### User Experience Considerations
Users can notice uncertainty because the interface shows a confidence bar and plays a confirmation sound when detection is stable.  
Misclassification may cause incorrect habit logs, which can impact the reliability and usefulness of the tracking system.  
If mistakes happen often, users may lose trust in the system or feel frustrated.

### Improvements / Optimizations

#### Sensing / Model Improvements
- Collect **more varied training data** (different lighting, background clutter).
- Train each class with **multiple object instances** (e.g., different cups, different fruit).
- Include training images where the target object is present **but not centered**, reflecting real use.

#### Interaction Layer Improvements
- Only confirm detection after **temporal smoothing** (already partly implemented).
- Add a small “preview” window showing the last captured frame when detection occurs → helps users verify logs.

#### System Redesign Possibility
- Combine **image recognition + simple movement cues** (e.g., pen tip motion vs static pen).
- For the black cup: use a **white marker/label** to add distinctive features for the model to latch onto.

#### Summary
This prototype successfully demonstrates automatic habit tracking using object-based activity recognition. However, real-world variability (especially color-based confusion and inconsistent lighting) significantly influences performance. The system benefits from temporal smoothing and user-facing feedback, but improving training data diversity and shifting the model to focus on shape rather than color will be necessary for robust everyday use.

### Part D
### Characterize your own Observant system

#### What can we use this system for?
We can use it for hands-free habit tracking. The system can detect daily activities (such as studying, drinking water, reading, taking vitamins, etc.) and automatically record the time spent on each activity. It is good for people who want to track routines without manually starting or stopping timers.

#### What is a good environment for this system?
The system works well under stable lighting, a clear camera view, and when the target object is held or placed within a reasonable distance. A desk with consistent lighting and fewer visually similar items nearby creates ideal conditions.

#### What is a bad environment for this system?
The system performs poorly in environments where:
- Lighting changes frequently (e.g., sunlight shifting)
- Background is cluttered with visually similar objects
- The camera is too far away or shaking
- The target object has similar color to surrounding items

#### When will the system break?
It will break when it cannot distinguish between two visually similar objects.  
For example, the black cup may be confused with any other black object, and the orange may be confused under warm lighting conditions.

#### How will it break?
When it breaks, it does not crash. Instead, it **misclassifies** or **oscillates** between two labels, leading to incorrect time logs or short unintended activity segments.

#### Other properties and behaviors
- It is sensitive to **color** more than object **shape**.
- It becomes more stable when temporal smoothing is applied.
- The system "feels" like it needs guidance — it benefits from feedback loops, clear lighting, and deliberate user positioning.

#### How does the system feel (as an interaction experience)?
It feels helpful when it works because it reduces user effort and makes habit tracking automatic.
However, it can feel fragile or uncertain in situations where the environment changes, which reminds the user that the system is not fully “intelligent,” but a responsive sensing material.

**\*\*\*Include a short video demonstrating the answers to these questions.\*\*\***
![8f00ab4868e8602b777adabdd3d8629](https://github.com/user-attachments/assets/46e706f4-5128-4359-9243-ab1f3209e5dd)
![9c1046616cdb9bdd87dc19746651921](https://github.com/user-attachments/assets/5e7bbf58-d279-4321-90f0-11d4a100a39e)

### Part 2.

Following exploration and reflection from Part 1, finish building your interactive system, and demonstrate it in use with a video.

#### Updated Improvement — More User-Friendly Web Interaction

In the improved version of our system, we added a **web-based user interface** to make the interaction clearer and more accessible.  
Instead of only recording the moment when an action is detected, the system now:

- **Starts a timer** automatically when a specific activity is recognized.
- **Displays a live timer** on the webpage so the user can see how long they have been doing the activity.
- **Stops the timer** when the system detects that the activity has ended (confidence drops).
- **Automatically logs the total duration** into the habit tracking record.

This improvement makes the system **much more user-friendly**, because users no longer need to manually enter or estimate how long they have been performing the activity.  
In many traditional habit-tracking apps, the user must remember to:
1) start the timer  
2) stop the timer  
3) write down the activity duration  

#### Benefits of This Change
- Reduces **user input effort** — truly hands-free habit tracking.
- Produces **more accurate time data**, especially for activities that are easy to forget.
- Makes the system feel like a **real interactive assistant** instead of only a detector.
- Helps users build habits more smoothly because **tracking becomes automatic**.

This enhancement not only improves usability but also makes the system more aligned with real-life habit-tracking needs.

https://github.com/user-attachments/assets/8dff075a-bf6b-481c-9ff9-bdec297ae944

