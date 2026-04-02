# Clean Stream Pro Wash - Ad Creative Strategy & Ideas

## What's Working (Based on Industry Data for Exterior Cleaning)

**IMAGE ads outperform video ads** for local service businesses in lead gen campaigns.
Here's why and what to shoot:

---

## HIGH-CONVERTING IMAGE AD IDEAS TO CREATE

### 1. Before/After Split Images (HIGHEST CONVERTING)
**Why:** Instant visual proof. The viewer's brain processes it in <1 second.

**What to shoot:**
- House siding: dirty left half → clean right half (same angle, same shot)
- Driveway: half cleaned, half dirty (shot from above or eye-level)
- Roof: show the black streak side vs the clean side
- Gutters: show the clogged gutter vs the clean gutter with water flowing

**Pro tips:**
- Shoot in the SAME lighting (don't fake it)
- Use a straight vertical line to split — looks more dramatic
- Include a recognizable Michigan-looking home (people need to see "that looks like MY house")
- Add simple text overlay: "Same house. 3 hours apart."

### 2. The "Transformation Carousel" (Swipe Ads)
Create a carousel (multiple images people swipe through):
- Image 1: "Think your house looks fine? Swipe →"
- Image 2: Close-up of algae/dirt on siding
- Image 3: The wash in progress (action shot with your equipment)
- Image 4: The finished result - gleaming clean
- Image 5: "FREE Quote - Tap below"

### 3. Testimonial/Social Proof Images
**What to create:**
- Screenshot a 5-star Google review, put it on a branded background
- Photo of the completed job with the homeowner (with permission)
- Text overlay: "Another happy customer in [neighborhood/city name]"

**Why it works:** People trust other people in their area. Use real city names like:
Caledonia, Byron Center, Kentwood, Wyoming, Grandville, Grand Rapids, Jenison, Hudsonville, Ada, Lowell

### 4. Seasonal Urgency Images
**Spring (March-May):**
- "Winter left its mark on your home. Let us fix it."
- Show a house with visible winter grime, pollen, mildew

**Summer (June-August):**
- "BBQ season is here. Is your deck guest-ready?"
- "Your neighbors already booked. Have you?"

**Fall (September-November):**
- "Get your gutters cleaned before the first freeze"
- "Last chance to wash before winter"

**Christmas Lighting (September-December):**
- "We book up by October 15th. Don't wait."
- Show a stunning install at dusk — lights glowing, blue hour sky

### 5. "The Gross Close-Up"
This STOPS the scroll. Take a macro/close-up photo of:
- Black algae on a roof shingle
- Mold growing on vinyl siding
- Green slime in a gutter
- Oil stains on concrete

Then the ad copy says: "This is growing on YOUR house right now. Want to see?"

### 6. Local Identity Ads
- "Proudly serving Caledonia & surrounding areas"
- Photo of your truck/trailer with branding in a recognizable local spot
- "Your local exterior cleaning experts - not a franchise, not a chain"

---

## AD COPY FORMULAS THAT GET LOW-CPL LEADS

### Formula 1: Problem → Agitate → Solve
> "See those black streaks on your roof? That's not dirt — it's algae eating your shingles. Every month you wait, it gets worse (and more expensive to fix). Clean Stream Pro Wash removes it safely with our soft wash system. No damage. No pressure. Just results. Get your FREE quote 👇"

### Formula 2: Social Proof → Offer
> "We just finished washing 3 homes on [Street Name] in Byron Center. The whole block looks amazing. Want your house to match? Free quotes for all homes in the Caledonia/Grand Rapids area. Tap below 👇"

### Formula 3: Urgency → Scarcity
> "We only have 8 spots left for house washing this month. Spring is our busiest season and we book up fast. Lock in your FREE quote before we're full. Serving 25 miles around Caledonia. 👇"

### Formula 4: Question Hook
> "When was the last time your house was washed? If you can't remember... it's time. Clean Stream Pro Wash | Free Quotes | Caledonia & Surrounding Areas 👇"

---

## CHRISTMAS LIGHTING SPECIFIC IDEAS

### Image Ideas:
1. **Dusk shot of a completed install** — the golden hour/blue hour glow makes Christmas lights look INCREDIBLE. This is your money shot.
2. **Before/after of a home at night** — dark house → lit up beautifully
3. **Close-up of commercial-grade LEDs** — show the quality difference vs store-bought
4. **Your crew on a ladder mid-install** — shows professionalism
5. **Neighborhood shot** — multiple houses you've done on the same street

### Copy Ideas:
- "Skip the ladder this year. We handle everything."
- "Your home, but make it the best on the block."
- "We're already 60% booked for the season. Claim your spot."
- "Professional Christmas lights. Installed, maintained, and removed. You just enjoy them."

---

## LEAD FORM BEST PRACTICES

Your current house washing lead form sounds solid. Key principles:
1. **Keep it SHORT** — Name, phone, email + 1-2 qualifying questions max
2. **Use multiple choice** — don't make them type. Dropdowns/buttons only.
3. **Qualifying questions filter tire-kickers:**
   - "When do you need service?" → "ASAP" = hot lead, "Just getting a quote" = warm
   - "Home square footage?" → Helps you quote faster
4. **Thank you page should set expectations:** "We'll call you within 24 hours"
5. **Context card** (the info screen before the form) should list 3-4 trust signals

---

## WEEKLY AD MANAGEMENT ROUTINE

1. **Monday:** Run `python3 audit.py` — check weekend performance
2. **Wednesday:** Run `python3 optimize.py --dry-run` — see what should change
3. **Friday:** Run `python3 optimize.py` — make changes, pause losers
4. **Monthly:** Run `python3 consolidate_winners.py` — refresh winner campaigns
5. **As needed:** Create new ads when you have fresh photos/content

---

## IMAGE AD CREATION CHECKLIST

When you shoot content for ads:
- [ ] Shoot before AND after (same angle, same lighting)
- [ ] Get at least one "in progress" action shot
- [ ] Capture the home from the street (shows full transformation)
- [ ] Get a close-up of the worst spot (the "gross" shot)
- [ ] If the customer is happy, get them in the photo (social proof)
- [ ] Note the city/neighborhood for localized ad copy
- [ ] Shoot in landscape AND square format (square works best on mobile)

Then run:
```bash
python3 create_ads.py --service "House Washing" --image your-photo.jpg
```

---

## BUDGET RECOMMENDATIONS

For a local service business in your area:
- **Testing new creatives:** $10-15/day per ad set
- **Scaling winners:** $25-50/day per winning ad set  
- **Total monthly budget suggestion:** $300-600/month to start
- **Goal CPL:** Under $15 for exterior cleaning, under $25 for Christmas lighting
- **Kill threshold:** Any ad that spends 2x your target CPL with zero leads = turn it off
