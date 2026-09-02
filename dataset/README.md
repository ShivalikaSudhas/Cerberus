# Known Face Dataset Directory

Store photos of authorized residents / users here in individual named folders.

### Folder Structure Example:
```text
dataset/
├── Alice/
│   ├── photo1.jpg
│   └── photo2.jpg
├── Bob/
│   ├── photo1.jpg
│   └── photo2.jpg
└── README.md
```

- Each folder name becomes the person's recognized label (e.g. `Alice`, `Bob`, `User_1`).
- Supported formats: `.jpg`, `.jpeg`, `.png`.
- The system automatically trains face signatures on startup or when pressing **`r`** in the live viewer window.
