# Everlights v3 for Home Assistant

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/everlights-dark.png">
    <img src="assets/everlights-light.png" alt="Everlights v3" width="300">
  </picture>
</p>

Home Assistant integration for Everlights v3 permanent holiday lights.

> [!WARNING]
> **Local control no longer works on bridge firmware B5010 (released 2026-10-30).** Everlights removed the local API on purpose and moved control to their cloud; they have confirmed this to users (see [issue #4](https://github.com/theOrakle/everlightsv3/issues/4)). On B5010 every control endpoint (`/v1/zones`, `/v1/sequences`, ...) returns `410 Gone` with `{"cloud": true}`, so this integration can no longer set colours or effects and fails setup with "will retry". Only a read-only status page (`GET /v1`) still answers. Bridges often update themselves, so check yours in the Everlights app. There is no known way to downgrade. Local control will return only if Everlights restores it; if you want it back, please ask [Everlights support](https://myeverlights.com/contact-support/). Cloud support is not planned yet.

It talks to your Everlights bridge on the local network (no cloud). This only works with bridge firmware older than B5010 (see the notice above). Each zone becomes a device with a light entity (colour and effect control) and diagnostic sensors for signal strength and the last request and response timestamps. The bridge is polled every 30 seconds.

**Note: This will override the existing everlights domain.  DO NOT USE if you use the older version from the core components.**

# Installation

There are two main ways to install this custom component within your Home Assistant instance:

1. Using HACS (see https://hacs.xyz/ for installation instructions if you do not already have it installed):

   1. From within Home Assistant, click on the link to **HACS**
   2. Click the three-dot menu (⋮) in the top right corner and select **Custom repositories**
   3. Enter the URL for this repository in the section that says _Add custom repository URL_ and select **Integration** in the _Category_ dropdown list
   4. Click the **ADD** button
   5. Close the _Custom repositories_ window
   6. Search for **Everlights v3** in HACS and select it from the results (HACS uses a single unified search/filter list rather than separate category tabs)
   7. Click to download/install it, and proceed with any on-screen instructions
   8. Restart your Home Assistant instance and then proceed to the _Configuration_ section below.

2. Manual Installation:
   1. Download or clone this repository
   2. Copy the contents of the folder **custom_components/everlights** into the same file structure on your Home Assistant instance
      - An easy way to do this is using the [Samba add-on](https://www.home-assistant.io/getting-started/configuration/#editing-configuration-via-sambawindows-networking), but feel free to do so however you want
   3. Restart your Home Assistant instance and then proceed to the _Configuration_ section below.

While the manual installation above seems like less steps, it's important to note that you will not be able to see updates to this custom component unless you are subscribed to the watch list. You will then have to repeat each step in the process. By using HACS, you'll be able to see that an update is available and easily update the custom component.

# Configuration

There is a config flow for this integration. After installing the custom component:

1. Go to **Settings** → **Devices & services**
2. Click **+ Add integration** (bottom right) to set up a new integration
3. Search for **Everlights v3** and click on it
4. You will be guided through the rest of the setup process via the config flow

# Development Releases

If you are developing locally and publishing through GitHub Releases:

1. Finalize code changes.
2. Run `./scripts/release.sh [patch|minor|major] ["commit message"]`.
3. If push fails due network/session issues, run `./scripts/push-release.sh [tag]`.
4. Create the GitHub Release from the pushed tag.

# Actions

This integration does not provide any actions. Control devices through the entities it creates (for example with the standard `switch`, `light`, `select` or `climate` actions).

# Removing the integration

1. Go to **Settings** → **Devices & services**, open **Everlights v3**, click the three-dot menu (⋮) next to the entry and choose **Delete**. The Everlights bridge entry, its devices and its entities are removed.
2. If you installed through HACS, open **HACS**, find **Everlights v3**, click the three-dot menu (⋮) and choose **Remove**. For a manual install, delete the **custom_components/everlights** folder instead.
3. Restart Home Assistant.

---
