---
name: Aetheria Reading System
colors:
  surface: '#fbfaee'
  surface-dim: '#dbdbcf'
  surface-bright: '#fbfaee'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f4e8'
  surface-container: '#efeee3'
  surface-container-high: '#e9e9dd'
  surface-container-highest: '#e4e3d7'
  on-surface: '#1b1c15'
  on-surface-variant: '#474740'
  inverse-surface: '#303129'
  inverse-on-surface: '#f2f1e5'
  outline: '#78776f'
  outline-variant: '#c8c7bd'
  surface-tint: '#5f5f57'
  primary: '#44453d'
  on-primary: '#ffffff'
  primary-container: '#5c5c54'
  on-primary-container: '#d6d4ca'
  inverse-primary: '#c8c7bd'
  secondary: '#655d51'
  on-secondary: '#ffffff'
  secondary-container: '#e9decf'
  on-secondary-container: '#696255'
  tertiary: '#484346'
  on-tertiary: '#ffffff'
  tertiary-container: '#605a5e'
  on-tertiary-container: '#dbd2d7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e4e3d8'
  primary-fixed-dim: '#c8c7bd'
  on-primary-fixed: '#1b1c16'
  on-primary-fixed-variant: '#474740'
  secondary-fixed: '#ece1d2'
  secondary-fixed-dim: '#cfc5b6'
  on-secondary-fixed: '#201b12'
  on-secondary-fixed-variant: '#4c463b'
  tertiary-fixed: '#e9e0e5'
  tertiary-fixed-dim: '#cdc4c9'
  on-tertiary-fixed: '#1e1a1e'
  on-tertiary-fixed-variant: '#4b4549'
  background: '#fbfaee'
  on-background: '#1b1c15'
  surface-variant: '#e4e3d7'
typography:
  headline-xl:
    fontFamily: Source Serif 4
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Source Serif 4
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Source Serif 4
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Be Vietnam Pro
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 30px
  body-md:
    fontFamily: Be Vietnam Pro
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  label-sm:
    fontFamily: Be Vietnam Pro
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  margin-mobile: 20px
  margin-desktop: 64px
  max-width-reading: 680px
---

## Brand & Style

The design system is centered on the concept of "Digital Quietude." It aims to bridge the gap between the tactile warmth of a physical library and the efficiency of a digital archive. The target audience is academic researchers, casual readers, and bibliophiles who spend extended periods engaged with long-form text.

The style is **Tactile Minimalism**. It avoids the sterile coldness of typical SaaS platforms by using organic textures, soft transitions, and "ink-on-paper" contrast levels. The goal is to lower the cognitive load and reduce ocular fatigue through a "Soft UI" approach that prioritizes content over container.

## Colors

The palette is anchored in a "Cream and Charcoal" philosophy to eliminate the harsh blue-light glare of pure white (#FFFFFF). 

- **Primary:** A muted, warm charcoal used for primary actions and headings.
- **Secondary:** An earthy taupe used for secondary metadata and borders.
- **Neutral/Background:** A soft cream (#FDFCF0) that mimics high-quality book paper.
- **Dark Mode:** Deep charcoal (#1A1A1A) provides the base, utilizing soft greys for text to ensure contrast remains comfortable rather than jarring.

Avoid pure blacks and pure whites. All interface colors should feel "tinted" by a physical material property.

## Typography

This design system employs a hybrid typographic approach. **Source Serif 4** provides a scholarly, authoritative, yet "human" feel for titles and headings, echoing traditional typesetting. 

For the body and functional UI elements, **Be Vietnam Pro** is used. Its slightly organic curves and generous x-height make it exceptionally legible for long-form reading on screens without feeling clinical.

- **Reading Rhythm:** Line heights for body text are intentionally loose (1.6x - 1.7x) to prevent line-skipping during deep reading sessions.
- **Mobile Scale:** On mobile devices, `headline-xl` should scale down to 32px to ensure titles do not break awkwardly.

## Layout & Spacing

The layout follows a **Fluid Content Model** with strict constraints on line length. Reading views are centered with a `max-width-reading` of 680px to maintain optimal characters-per-line (CPL).

- **Grid:** A 12-column grid is used for browsing views (library shelves, search results).
- **Margins:** Generous "safe zones" are used to give content room to breathe, echoing the wide margins of luxury editions.
- **Rhythm:** Spacing increments are based on a 4px baseline, but primary groupings should favor `xl` (40px) padding to reinforce the minimalist, airy aesthetic.

## Elevation & Depth

Elevation in this design system is expressed through **Tonal Layering** and **Soft Ambient Shadows**. 

- **Surface 1:** The base page (Cream).
- **Surface 2:** Raised cards or menus use a slightly lighter tint or pure white with a very diffused, low-opacity shadow (Color: Primary, Opacity: 4%, Blur: 20px).
- **Interactive Depth:** Buttons should feel "tucked into" the surface rather than sitting high above it. Use subtle inner shadows for pressed states to mimic a physical depression in paper.
- **Glassmorphism:** Use sparingly for navigation bars (15px blur, 80% opacity) to maintain context of the scroll position without distracting from the text.

## Shapes

The shape language is **Rounded**, avoiding sharp corners that feel aggressive or clinical. 

- **Containers:** Cards and primary containers use `rounded-lg` (1rem).
- **Interactive Elements:** Buttons and input fields use `rounded` (0.5rem).
- **Small Elements:** Chips and badges use `rounded-xl` (1.5rem) to create a "pebble" effect.
- **Media:** Book covers and imagery should have a slight 4px radius to soften their appearance while maintaining the rectangular integrity of a book.

## Components

- **Buttons:** Primary buttons use the Charcoal color with the Cream text. Secondary buttons are outlined with a 1px stroke in the Secondary color. All buttons have a subtle transition (200ms ease-in-out).
- **Reading Progress:** A thin, non-intrusive progress bar at the top of the viewport using the Primary color.
- **Cards:** Book cards should feature the cover as the hero element, with metadata set in `label-sm`. The card background should be a subtle shift from the main background to denote clickability.
- **Inputs:** Text fields use a soft-filled background (slightly darker than the page) rather than a heavy border. The focus state is indicated by a 1px Primary color bottom-border.
- **Annotations:** Highlighted text should use a semi-transparent tint of a "highlighter yellow" or "ink blue" that maintains text contrast.
- **Lists:** Clean, borderless list items with generous vertical padding (16px) and a subtle separator line (Opacity: 10%).