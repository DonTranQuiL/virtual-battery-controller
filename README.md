<div align="center">

# 🔋 Virtual Battery Controller (VBC)
### Turn your Home into a Thermal Battery for Smart Energy Arbitrage
</div>
<p align="center">
  <!-- Release / License -->
  <a href="https://github.com/DonTranQuiL/virtual-battery-controller/releases">
    <img src="https://img.shields.io/github/v/release/DonTranQuiL/virtual-battery-controller?style=for-the-badge&color=007ec6" alt="Latest Release">
  </a>
  <a href="https://github.com/DonTranQuiL/virtual-battery-controller/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/DonTranQuiL/virtual-battery-controller?style=for-the-badge&color=007ec6" alt="License">
  </a>

  <!-- CI / Quality -->
  <a href="https://github.com/DonTranQuiL/virtual-battery-controller/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DonTranQuiL/virtual-battery-controller/codechecker.yml?style=for-the-badge&label=CODE%20CHECKS&color=5dbb0f" alt="Code Checks">
  </a>
  <a href="https://github.com/DonTranQuiL/virtual-battery-controller/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DonTranQuiL/virtual-battery-controller/pytest.yml?style=for-the-badge&label=TESTS&color=5dbb0f" alt="Tests">
  </a>
  <a href="https://github.com/DonTranQuiL/virtual-battery-controller/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DonTranQuiL/virtual-battery-controller/hacs.yaml?style=for-the-badge&label=HACS%20VALIDATION&color=5dbb0f" alt="HACS Validation">
  </a>

  <!-- Code Quality -->
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-5dbb0f?style=for-the-badge" alt="pre-commit">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/badge/code%20style-ruff-000000?style=for-the-badge" alt="Ruff">
  </a>
  <a href="https://codecov.io/gh/DonTranQuiL/virtual-battery-controller">
  <img 
    src="https://codecov.io/gh/DonTranQuiL/virtual-battery-controller/branch/main/graph/badge.svg"
    alt="Coverage"
    style="height:28px;"
  >
</a>

  <!-- Ecosystem -->
  <a href="https://hacs.xyz/">
    <img src="https://img.shields.io/badge/HACS-CUSTOM-ff6e27?style=for-the-badge" alt="HACS">
  </a>
  <a href="https://www.home-assistant.io/">
    <img src="https://img.shields.io/badge/Home%20Assistant-2024.5%2B-007ec6?style=for-the-badge" alt="Home Assistant">
  </a>

  <!-- Social / Support -->
  <a href="https://github.com/DonTranQuiL">
    <img src="https://img.shields.io/badge/maintainer-%40DonTranQuiL-007ec6?style=for-the-badge" alt="Maintainer">
  </a>
  <a href="https://ko-fi.com/DonTranQuiL">
    <img src="https://img.shields.io/badge/buy%20me%20a%20coffee-donate-ffdd00?style=for-the-badge" alt="Donate">
  </a>
  <a href="https://community.home-assistant.io/">
    <img src="https://img.shields.io/badge/community-forum-007ec6?style=for-the-badge" alt="Community">
  </a>
</p>

</div>

<div align="center">
  
**Virtual Battery Controller** is a sophisticated Home Assistant integration that transforms your climate-controlled rooms and smart appliances into a unified "Virtual Battery." By leveraging thermal mass and price forecasting, it automatically "charges" your home when energy is cheapest or when solar export is high, and "discharges" when prices peak.

</div>

---

## 🚀 Key Features

*   **Dynamic Price Arbitrage:** Automatically identifies the cheapest 25% of hours every day using 24-hour price forecasts from ENTSO-E, Enever, or Nord Pool.
*   **Solar Export Matching:** Instantly forces "charging" if your solar panels are exporting more energy than your device's wattage, ensuring no green energy goes to waste.
*   **Thermal State of Charge (SoC):** Provides a real-time percentage sensor showing how "full" your thermal battery is based on room temperature relative to your set limits.
*   **Unified Device Management:** All sensors, binary sensors, and controls are grouped under a single "Virtual Battery" device for a clean, professional dashboard experience.
*   **Multi-Device Control:** Synchronize a climate entity (Airco/Heat Pump) and an unlimited number of smart plugs or relays simultaneously.
*   **Native Options Menu:** Change your target devices, temperature limits, or wattage on the fly without ever restarting Home Assistant.

---

## 🛠️ How it Works

The integration operates on the principle of **Thermal Mass Storage**. 

### 1. The Decision Engine
The VBC monitors your configured price sensor. It calculates the 25% quantile (the "cheap" threshold) of the daily price data. If the current price is below that threshold, or if your solar panels are exporting enough power to cover the device's wattage, the "Charging" binary sensor flips to **ON**.

### 2. The Execution
*   **Heating Mode:** When charging, the VBC pushes your thermostat to the **Max Temp**. When discharging, it drops to the **Min Temp**.
*   **Cooling Mode:** When charging, it pushes the thermostat to the **Min Temp** (storing cold). When discharging, it lets it rise to the **Max Temp**.
*   **Smart Plugs:** Any connected relays or plugs (Boilers, Pool Pumps, EV chargers) are toggled to match the charging state.

### 3. Financial Feedback
The integration logs estimated savings to your Home Assistant logs in real-time, showing you exactly how much money you are saving by shifting your loads to the cheapest hours.

---

## 📦 Installation

### Option 1: HACS (Recommended)
1. Open **HACS** > **Integrations**.
2. Click the three dots in the top right and select **Custom repositories**.
3. Add `https://github.com/DonTranQuiL/virtual-battery-controller` with Category: `Integration`.
4. Click **Install**.
5. Restart Home Assistant.

### Option 2: Manual
1. Download the `virtual_battery_controller` folder.
2. Copy it into your `custom_components` directory.
3. Restart Home Assistant.

---

## ⚙️ Configuration

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration** and search for **Virtual Battery Controller**.
3. Follow the UI prompts to select your sensors and set your temperature bounds.

> **Tip:** You can click the **Configure** gear icon on the integration at any time to update your settings without a restart!

---

## 📊 Sensors Provided

| Entity | Description |
| :--- | :--- |
| `binary_sensor.virtual_battery_arbitrage_charging` | High if energy is cheap or solar is available. |
| `sensor.virtual_battery_state_of_charge` | 0–100% SoC based on thermal storage. |

---

## 🤝 Contributing
Contributions are welcome! Whether it's adding support for more price providers or refining the SoC algorithm, feel free to open a PR.

**Developed by [@Malosaaa](https://github.com/Malosaaa)**

---

### Why use a Virtual Battery?
Conventional batteries are expensive and have limited cycles. Your home already has "mass"—walls, floors, and furniture—that holds temperature. By "over-heating" or "over-cooling" your home by just 1 or 2 degrees when energy is free or cheap, you are effectively storing kilowatts of energy for later use, reducing your carbon footprint and your electricity bill simultaneously.


