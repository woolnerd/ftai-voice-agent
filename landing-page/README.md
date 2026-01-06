# Voice AI Receptionist Landing Page

A clean, conversion-focused landing page with shadcn-inspired design for selling AI voice receptionist services.

## Quick Start

1. Open `index.html` in your browser to preview
2. Update the meta tags for your domain (see below)
3. Deploy to your hosting platform

## Already Configured

- **Phone Number**: 1-877-836-2098 (live demo)
- **Calendly Link**: https://calendly.com/dave-getfreetime/15min
- **Loom Video**: Real estate demo embedded in hero section
- **Contact Email**: dave@getfreetime.ai

## Customization

### 1. Update Meta Tags for Social Sharing

In `index.html` (lines 13 and 19), update the Open Graph and Twitter Card image URLs:

```html
<meta property="og:image" content="https://yourdomain.com/og-image.jpg">
<meta name="twitter:image" content="https://yourdomain.com/og-image.jpg">
```

Replace `https://yourdomain.com/og-image.jpg` with your actual domain and image path. Recommended image size: 1200x630px.

### 2. Customize Colors (Optional)

In `styles.css`, update the CSS variables at the top:

```css
:root {
    --primary-color: #2563eb;  /* Main CTA button color */
    --primary-hover: #1d4ed8;  /* Button hover color */
    /* ... other colors ... */
}
```

## Deployment

### Option 1: GitHub Pages
1. Commit the `landing-page` folder to your repo
2. Enable GitHub Pages in repo settings
3. Select the `landing-page` folder as source

### Option 2: Netlify
1. Drag and drop the `landing-page` folder to Netlify
2. Your site is live in seconds

### Option 3: Vercel
1. Import your repo to Vercel
2. Set root directory to `landing-page`
3. Deploy

### Option 4: Any Static Host
Upload the files to any web hosting service that supports static HTML.

## Features

- **shadcn-inspired design** - Modern, clean UI with professional components
- **Live phone demo** - Call 1-877-836-2098 to experience the AI (most powerful CTA)
- **Mobile responsive** - Works perfectly on all devices
- **Fast loading** - No frameworks, just clean HTML/CSS with Lucide icons
- **SEO ready** - Semantic HTML with Open Graph and Twitter Card meta tags
- **Conversion optimized** - Prominent phone CTA, clear benefit messaging, "Them vs Us" comparison

## Design Highlights

- **Hero Section**: Left-aligned headline with phone CTA and video embed on right
- **Problem/Solution Cards**: Color-coded with icons (red for problem, green for solution)
- **Live Demo Section**: Large phone number with pulsing icon animation
- **Cost Comparison**: Side-by-side cards showing competitor pricing vs yours
- **Features Grid**: 2-column layout with Lucide icons
- **Single CTA**: Focused conversion with one primary button

## File Structure

```
landing-page/
├── index.html       # Main HTML file with meta tags
├── styles.css       # shadcn-inspired CSS design system
├── favicon.svg      # Voice waveform icon
└── README.md        # This file
```

## Tips for Maximum Conversion

1. **The phone number IS your demo** - It's more powerful than any testimonial
2. **Update OG images** - Add a 1200x630px image for social sharing
3. **Test on mobile** - Most visitors will be on phones
4. **Track analytics** - Add Google Analytics or Plausible to measure performance
5. **Monitor call volume** - The phone demo will drive lots of calls

## Support

Questions? Email dave@getfreetime.ai
