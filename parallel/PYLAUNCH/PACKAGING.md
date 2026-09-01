# Packaging plan — `WOF Future Danger.exe`

Packaging is intentionally deferred until the live CDP path is proven once on the owner's Windows Browser session.

Recommended first package:

```bat
.venv\Scripts\python -m pip install pyinstaller
.venv\Scripts\pyinstaller --noconsole --onefile --name "WOF Future Danger" launcher.py
```

Before calling that distributable-ready:

1. add a real `.ico` asset owned by the project;
2. include version metadata;
3. decide whether settings move from CLI-only foundation fields into persisted local JSON;
4. optionally add Start-with-Windows and Start-minimized settings;
5. preserve localhost-only CDP and dedicated browser profile;
6. keep Assist Mode / one-key moves absent until a separate explicit post-foundation lane.

Do not bundle a browser unless the project intentionally chooses Chrome for Testing later. The foundation prefers installed Chrome/Edge and a dedicated WOF profile.
