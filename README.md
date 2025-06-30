To use the project, execute the script with the following command:

```
python app.py
```

then follow the link 

REMEMBER TO INSTALL FFMEG TO ENV VARIABLES

#### Step 1: Download FFmpeg Binary

1. Go to: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Under **"Release Builds"**, download **`ffmpeg-release-essentials.zip`**
3. Extract the zip — you'll get a folder like `ffmpeg-<version>-essentials_build`

---

#### Step 2: Add FFmpeg to System PATH

1. Go to the extracted folder → open the `bin` subfolder
2. Copy the full path (e.g., `C:\Users\saani\Downloads\ffmpeg\bin`)
3. Press `Win + S`, search for **“Environment Variables”**, and open it
4. In **System variables**, find `Path` → click **Edit** → click **New** and paste the path
5. Click OK on all dialogs

---

#### Step 3: Test It

Close any terminal or IDE and reopen it. Then run:

```bash
ffmpeg -version
```

You should now see the version info — which means it’s ready for use by your Python script.
