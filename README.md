# 🧩 Subdivision Controller Addon for Blender

**Author:** Awaken Idiotic  
**Version:** 1.0.1  
**Blender Compatibility:** 4.2.0+  
**Category:** Object

---

## 🧠 What is this?

The **Subdivision Controller** is a Blender addon that allows you to manage subdivision levels across multiple objects or collections with a single controller object. It’s especially useful for lookdev, layout, or rendering prep where consistent subdivision control is needed.

---

## ✨ Features

- 🔘 Create a controller empty to manage subdivision levels.
- 🎯 Target individual objects or entire collections.
- ➕ Add subdivision modifiers to meshes that don’t have one.
- ♻️ Update or delete modifiers from selected targets.
- 🧼 Set smooth or flat shading on all target meshes.
- 📊 Real-time stats panel shows how many objects/subdivisions exist.

---

## 🛠 How to Install

1. Download the `.py` file.
2. Open Blender.
3. Go to `Edit > Preferences > Add-ons`.
4. Click `Install`, then select the `Subd_Controller_Addon.py` file.
5. Enable the checkbox to activate it.

---

## 🧩 How to Use

### 📍 Create a Controller
- In the `Add > Create Sundivide Controller` menu (or Object menu), choose **Subdivision Controller**.

### 🗂 Set Targets
- In the controller object’s panel (`Object Properties` tab):
  - Enter object or collection names (comma-separated), or use the eyedropper to add selected ones.

### 🧩 Control Panel
- **Viewport** & **Render**: Set subdivision levels.
- **Optimize Display**: Enable control edges only.
- Buttons for:
  - ✅ Add modifiers
  - ♻️ Update modifiers
  - ❌ Remove modifiers
  - 🎨 Set shade smooth / flat
  - 🔍 View live stats

---

## 📥 Example Usage

- Target string: `House, Props, Table001`
- Control the subdivision of everything inside `Props` collection and object `Table001`.

---

## 🎓 Tutor
- YouTube: [[AwakenIdiotic](https://youtu.be/RliszHmfUIk)

---

## 📜 License

MIT License – Free to use, modify, and distribute.

---

## 💬 Contact

- Portfolio: [https://idiotic.artstation.com](https://idiotic.artstation.com)
- YouTube: [AwakenIdiotic](https://youtube.com/@AwakenIdiotic)
- Gumroad: [https://awakenidiotic.gumroad.com/l/SubdController](https://awakenidiotic.gumroad.com/l/SubdController)

Enjoy controlling your subdivision chaos 😎
