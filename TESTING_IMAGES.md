# Testing the Move Images Feature

## Quick Test Steps

1. **Open the app**: http://127.0.0.1:5000

2. **Select White Belt** (first belt card)

3. **Test Move Terms with Images**:
   - Card 11: "Front Stance" (앞굽이) - Should show stance image
   - Card 12: "Walking Stance" (앞서기) - Should show stance image
   - Card 13: "Low Block" (아래막기) - Should show block image
   - Card 14: "Middle Block" (몸통막기) - Should show block image
   - Card 15: "Front Kick" (앞차기) - Should show kick image
   - Card 16: "Middle Punch" (몸통지르기) - Should show strike image

4. **Test Non-Move Terms** (should work as before, no image):
   - Card 1: "Attention" (차렷) - No image
   - Card 2: "Bow" (경례) - No image
   - Card 3: "Ready Stance" (준비) - No image

5. **Check on Mobile**:
   - Open on iPhone/iPad
   - Images should scale appropriately
   - No layout breaking

## What to Look For

✅ **Images display** in white rounded container between translation and Korean text
✅ **Only move terms** show images (Stance, Kick, Block, Strike, Form)
✅ **Regular terms** (Command, Number, etc.) don't show images
✅ **Images scale** on hover (slight zoom)
✅ **Responsive** on mobile devices (smaller but still visible)
✅ **SVG quality** - Images are crisp at any size

## If Something's Wrong

**Images not showing?**
- Check browser console (F12) for errors
- Verify Flask server is running
- Check that image files exist in `/static/images/moves/`

**Layout broken?**
- Check mobile responsiveness in browser dev tools
- Verify CSS loaded correctly
- Clear browser cache (Cmd+Shift+R)

**Wrong images?**
- Verify terms.json has correct image_path values
- Check category field matches image map (Stance, Kick, Block, Strike, Form)

## Success Criteria

✅ 163 technique terms display visual demonstrations
✅ Images load quickly (SVG is lightweight)
✅ Flashcards still flip smoothly
✅ Mobile experience remains excellent
✅ Kids can see what techniques look like!

---

**Ready to test!** 🥋✨
