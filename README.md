AI Property Video Generator

Assignment track: AI Content Creation / Multimedia

1. Project overview

It is a Streamlit prototype that turns real-estate details and 4--8
visual assets into a short promotional property film. Users enter a
property name, location, optional asking price, property type, verified
features, and contact/call-to-action text. They upload photos, existing
walkthrough clips, and/or AI-generated image-to-video clips in the order
they want them to appear.

The app exports: - Vertical 9:16 MP4 (720 × 1280) for
Reels/Shorts. - Landscape 16:9 MP4 (1280 × 720) for websites and
YouTube. - Either format or both.

This is an assignment prototype, not a production-ready real-estate
platform.


2. Setup and run

Requirements
- Python 3.11 or 3.12 recommended.
- FFmpeg installed and available on your system PATH.
- Internet access if you enable gTTS narration.

Windows
1. Create and activate a virtual environment (recommended):
   python -m venv .venv
   .venv\Scripts\activate
2. Install dependencies:
   python -m pip install -r requirements.txt
3. Install FFmpeg and add its bin folder to PATH. Open a new
   Command Prompt after updating PATH.
4. Start the app:
   python -m streamlit run app.py
5. Open the local URL shown in the terminal, usually
   http://localhost:8501.
macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
Make sure FFmpeg is installed before rendering.
6. Dependencies and AI/API disclosure
  Dependency or service               Purpose
  Streamlit                           Web form, uploads, validation
                                      messages, preview and download
                                      controls

  MoviePy 2.x                         Reads/edits video, combines scenes,
                                      transitions and audio, exports MP4

  Pillow (PIL)                        Loads/crops images and draws title
                                      cards and text overlays

  gTTS                                Optional text-to-speech narration;
                                      requires internet

  FFmpeg                              Media decoding/encoding used by
                                      MoviePy

  Optional external image-to-video    May be used separately to animate a
  service                             still photo; its resulting MP4 is
                                  uploaded into the app
AI/model note: This code does not call a paid AI video-generation
API and does not need an API key. Captions and narration text are
created with template logic using only details entered by the user. gTTS
reads the script aloud; it does not write the script. If a separate AI
video tool is used, it is an optional external service and may have
usage limits or charges. Check its current terms before use.

4. How to use the app

1. Enter the property/listing name and location.
2. Add the asking price if known (optional).
3. Choose the property type.
4. Enter verified features separated by commas, such as
   sunlit living room, modular kitchen, private balcony.
5. Enter contact text or a call to action.
6. Upload 4--8 assets in the intended scene order. Supported
   image/video types: JPG, JPEG, PNG, MP4, MOV, M4V, WEBM and AVI.
7. Choose Vertical 9:16, Landscape 16:9, or both.
8. Optionally enable voice narration and choose English, Hindi, French
   or Spanish.
9. Optionally upload background music as MP3, WAV or M4A and set its
   volume.
10. Click Create cinematic property film.
11. Review the narration script, then click Render selected
    format(s).
12. Preview each output in the app and click its download button to save
    the MP4.

How the hybrid footage workflow works
- Photos: get a smooth 2D pan/zoom (Ken Burns-style) effect and
  text overlays.
- Real video: is trimmed to a scene duration, fitted to the output
  frame and given text overlays. The original camera motion is
  retained.
- AI-generated clips: create these separately with an
  image-to-video tool, download the MP4 and upload it with the real
  clips/photos. Lumière retains the clip's motion.
- Transitions: crossfades join scenes.
- Audio: optional gTTS narration and optional user-supplied music
  can be added.
This approach keeps local editing free of video-generation API charges.
It does not generate AI video inside the app.


5. Sample input for demo
Use fictional information and sample assets; do not include real
customer personal information.
  Field                               Example
  Property name                       The Willow Residence

  Location                            Chandigarh, Punjab

  Asking price                        ₹1.25 crore

  Property type                       3-BHK Apartment

  Verified features                   Sunlit living room, modular
                                      kitchen, private balcony

  Contact / CTA                       Contact us to schedule a private
                                      viewing

  Assets                              4--8 sample JPG/PNG photos and/or
                                      MP4 clips

  Output                              Vertical 9:16 and Landscape 16:9

  Narration                           English (optional)
  Music                               Licensed MP3/WAV/M4A (optional)
The property name, location, contact/CTA, 4--8 assets and at least one
output format are required. Price and features are optional. When
features are blank, generic captions are used instead of invented
property features.

Sample output: Run the workflow above to render a sample MP4. A
sample MP4 is not included in this source-code package, so render one
with fictional details and sample images before submitting the
assignment.


6. What the code does
The main code is app.py.
  Function or section                 What it does
  Streamlit form                      Collects property details, assets,
                                      output formats and optional audio
                                      settings

  clean_filename()                  Creates a safe output filename from
                                      the property name

  get_font(), wrap_text(),        Support styled, readable text
  draw_tracking()                   overlays

  cover_image(),                    Prepare/crop images and improve
  add_bottom_gradient()             contrast behind text

  make_scene() /                    Create photo-based scene graphics
  landscape_scene()                 for vertical and landscape output

  build_scene_plan()                Creates opening, feature and
                                      closing captions from user input

  make_motion_clip() /              Adds 2D pan/zoom motion to
  motion_clip_for_size()            still-image scenes

  fit_video_clip() /                Trims/fits video clips for the
  landscape_video_fit()             selected aspect ratio

  make_video_overlay() /            Adds text graphics over video
  landscape_overlay()               scenes

  render_video()                    Combines scenes, adds crossfades
                                      and optional audio, and writes MP4

  Validation and error handling       Checks required fields, asset
                                      count, format selection and image
                                      readability

  Preview/download section            Shows rendered videos and provides
                                  download buttons
Processing flow
Property details + 4–8 photos/video clips
                  |
                  v
          Validate inputs
                  |
                  v
      Build captions and scene plan
                  |
                  v
 Prepare photo scenes / fit video scenes
                  |
                  v
 Add pan-zoom, text overlays, crossfades
                  |
                  v
  Optional narration and background music
                  |
                  v
 Render vertical and/or landscape MP4 files
                  |
                  v
         Preview and download


7. Approach and key decisions
- Grounded captions: captions and narration use the property
  details entered by the user. The app does not intentionally invent
  property facts.
- Hybrid asset support: photos, real walkthrough footage and
  externally generated AI clips can be arranged together.
- Dual aspect ratios: each selected format is rendered separately
  to allow a format-specific layout.
- Cost control: no paid AI-video API is called by this code;
  generated clips are imported as files.
- Input checks: required text, the 4--8 asset range, output format
  selection and image readability are checked before rendering.
8. Limitations and quality checks
- The app edits and assembles media; it does not generate AI
  image-to-video clips itself.
- Photo pan/zoom is a 2D effect, not 3D reconstruction or true camera
  movement through a property.
- AI-generated clips can distort room geometry, furniture, windows or
  finishes. Inspect them before publishing.
- Video is center-cropped to fill the selected frame; inspect both
  aspect ratios for cut-off details.
- Rendering both formats takes longer than rendering one.
- gTTS requires internet and may have service availability limits.
- Use only media, music and logos that you own or are licensed to use.
- The app does not verify property claims; the user is responsible for
  accurate details.
- Test a complete render on the target computer before submitting.


9. Assignment submission checklist
- [ ] Run the app successfully.
- [ ] Use fictional/anonymized property details.
- [ ] Upload 4--8 sample visual assets and render at least one MP4.
- [ ] Test preview and download.
- [ ] Test both formats if possible.
- [ ] Submit source code and this README.
- [ ] Include a rendered sample MP4 as a separate file.
- [ ] Be ready to explain template captions, pan/zoom, video
  processing, transitions, audio and limitations.
- [ ] Do not include API keys, passwords or real customer personal
  information.


10. Project files
- app --- Streamlit application.
- requirements.txt --- Python dependencies.
- README.md --- setup, usage, implementation explanation and limitations.