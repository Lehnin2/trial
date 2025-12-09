# 🎨 Enhanced Features Guide

## New Capabilities

Your PowerPoint Compliance Checker now has **powerful new features**:

### ✨ What's New

1. **📖 PowerPoint Preview** - View slides before checking
2. **🎯 Selective Module Checking** - Choose which rules to validate
3. **👁️ Side-by-Side View** - See slides with violations highlighted
4. **📍 Slide-Specific Violations** - Violations mapped to exact slides
5. **🎨 Visual Indicators** - Color-coded slide thumbnails

---

## 🚀 New Workflow

### Old Workflow
```
Upload → Wait → View All Results
```

### New Enhanced Workflow
```
Upload → Preview Slides → Select Modules → Check → View Results by Slide
```

---

## 📖 Feature 1: PowerPoint Preview

### What It Does
- Extracts and displays all slides from your PowerPoint
- Shows slide titles and content
- Allows navigation through slides before checking

### How to Use
1. Upload PowerPoint and metadata files
2. Click "Upload & Preview"
3. Browse through slides using the thumbnail list
4. Review content before running checks

### Benefits
- Verify correct file uploaded
- Understand document structure
- Plan which modules to run

---

## 🎯 Feature 2: Selective Module Checking

### What It Does
- Choose specific compliance modules to run
- Skip modules that aren't relevant
- Faster processing for targeted checks

### Available Modules
1. **Structure** - Document format and layout
2. **Registration** - Fund registration requirements
3. **ESG** - ESG compliance
4. **Disclaimers** - Required disclaimers
5. **Performance** - Performance rules
6. **Values** - Securities mentions
7. **Prospectus** - Prospectus alignment
8. **General** - General rules

### How to Use
1. After uploading, you'll see the module selection panel
2. Click modules to toggle selection (green = selected)
3. Use "Select All" / "Deselect All" for quick changes
4. Click "Run Compliance Check" with your selection

### Use Cases

**Quick Structure Check**
- Select only "Structure" module
- Fast validation of document format
- Perfect for initial reviews

**ESG Focus**
- Select "ESG" + "Disclaimers"
- Targeted ESG compliance check
- Faster than full validation

**Performance Review**
- Select "Performance" + "Values"
- Focus on performance disclosures
- Skip unrelated modules

**Full Compliance**
- Select all 8 modules
- Comprehensive validation
- Same as before, but with preview

---

## 👁️ Feature 3: Side-by-Side View

### What It Does
- Shows slides and violations together
- Navigate slides to see their specific issues
- Visual connection between content and violations

### Layout

```
┌─────────────┬──────────────┬─────────────────┐
│   Slide     │    Slide     │   Violations    │
│ Thumbnails  │   Preview    │   for Slide     │
│             │              │                 │
│  1 [🔴]     │  Title: ...  │  🔴 STRUCT_001  │
│  2 [🟢]     │              │  🟠 ESG_003     │
│  3 [🟠]     │  Content:... │  🟡 PERF_012    │
│  4 [🟢]     │              │                 │
│  ...        │              │  [Details...]   │
└─────────────┴──────────────┴─────────────────┘
```

### How to Use
1. After compliance check completes
2. Click any slide thumbnail on the left
3. Center shows slide content
4. Right shows violations for that slide
5. Navigate through slides to review all issues

### Benefits
- **Context**: See violations in context of slide content
- **Efficiency**: Focus on problematic slides
- **Clarity**: Understand exactly where issues are
- **Navigation**: Jump directly to slides with issues

---

## 📍 Feature 4: Slide-Specific Violations

### What It Does
- Each violation is mapped to its exact slide number
- Slide thumbnails show violation severity
- Filter violations by slide

### Visual Indicators

**Slide Thumbnail Colors:**
- 🔴 **Red** - Has critical violations
- 🟠 **Orange** - Has major violations
- 🟡 **Yellow** - Has minor violations only
- 🟢 **Green** - No violations

### How to Use
1. Look at slide thumbnails
2. Red/orange slides need immediate attention
3. Click slide to see its specific violations
4. Fix issues slide by slide

### Example
```
Slide 1 [🔴] - Cover Page
  └─ STRUCT_001: Missing fund name (Critical)
  └─ STRUCT_002: Missing date (Major)

Slide 2 [🟢] - No issues

Slide 3 [🟠] - Performance
  └─ PERF_005: Missing disclaimer (Major)

Slide 4 [🟡] - ESG
  └─ ESG_012: Formatting issue (Minor)
```

---

## 🎨 Feature 5: Enhanced UI

### New Components

**1. Module Selection Panel**
- Checkbox-style selection
- Module descriptions
- Count of selected modules
- Select/Deselect all button

**2. Slide Navigator**
- Thumbnail list with indicators
- Current slide highlighting
- Violation count per slide
- Click to navigate

**3. Slide Preview**
- Title display
- Content extraction
- Clean, readable format
- Responsive layout

**4. Violation Sidebar**
- Slide-specific violations
- Expandable details
- Color-coded severity
- Quick actions

---

## 📊 Comparison: Old vs New

### Old Interface
```
Upload → Processing → All Violations List
```
- No preview
- All modules always run
- Flat violation list
- No slide context

### New Interface
```
Upload → Preview → Select Modules → Processing → Slide-by-Slide Results
```
- ✅ Preview slides first
- ✅ Choose modules
- ✅ Faster targeted checks
- ✅ Violations mapped to slides
- ✅ Visual indicators
- ✅ Better navigation

---

## 🎯 Use Case Examples

### Use Case 1: Quick Format Check
**Scenario**: You just want to verify document structure

**Steps**:
1. Upload files
2. Preview slides (optional)
3. Select only "Structure" module
4. Run check (30 seconds instead of 5 minutes)
5. Review structure violations

**Time Saved**: 90%

---

### Use Case 2: ESG Compliance Review
**Scenario**: Focus on ESG requirements

**Steps**:
1. Upload files
2. Preview to understand content
3. Select "ESG" + "Disclaimers" modules
4. Run targeted check
5. Review ESG-specific issues by slide

**Benefits**: Focused, faster, clearer

---

### Use Case 3: Slide-by-Slide Review
**Scenario**: Fix violations one slide at a time

**Steps**:
1. Run full compliance check
2. Look at slide thumbnails
3. Start with red (critical) slides
4. Click slide → see violations → fix
5. Move to orange (major) slides
6. Finally yellow (minor) slides

**Workflow**: Organized, prioritized, efficient

---

### Use Case 4: Pre-Meeting Quick Check
**Scenario**: Meeting in 10 minutes, need quick validation

**Steps**:
1. Upload files
2. Select "Structure" + "Disclaimers" (most critical)
3. Run check (1-2 minutes)
4. Review critical issues only
5. Fix before meeting

**Result**: Fast, focused, actionable

---

## 🔧 Technical Details

### New API Endpoints

**POST /api/upload-preview**
- Uploads files without processing
- Returns slide preview data
- Creates job ID for later use

**POST /api/check-modules**
- Runs selected modules only
- Accepts comma-separated module list
- Uses existing job ID

**GET /api/slides/{job_id}**
- Returns slide preview data
- Extracts titles and content
- Provides structure information

### Module Selection Format
```javascript
// All modules
modules: "all"

// Specific modules
modules: "Structure,ESG,Performance"

// Single module
modules: "Structure"
```

---

## 💡 Tips & Best Practices

### Tip 1: Preview First
Always preview slides before checking to:
- Verify correct file
- Understand structure
- Plan module selection

### Tip 2: Start Small
For first-time checks:
1. Run "Structure" only
2. Fix structural issues
3. Then run other modules
4. Avoid overwhelming results

### Tip 3: Use Color Codes
- Focus on red slides first (critical)
- Then orange (major)
- Finally yellow (minor)
- Green slides are good!

### Tip 4: Targeted Checks
Don't always run all modules:
- Structure check: 30 seconds
- ESG check: 1 minute
- Full check: 5 minutes
- Choose based on needs

### Tip 5: Slide-by-Slide Fixes
Fix violations slide by slide:
1. Click slide with issues
2. Read violations
3. Fix in PowerPoint
4. Re-upload and check
5. Repeat until clean

---

## 🐛 Troubleshooting

### Preview Not Showing
**Problem**: Slides don't display after upload

**Solution**:
- Check file is .pptx (not .ppt)
- Verify file isn't corrupted
- Check browser console for errors
- Try smaller file first

---

### Module Selection Not Working
**Problem**: Can't select/deselect modules

**Solution**:
- Refresh page
- Clear browser cache
- Check if JavaScript is enabled
- Try different browser

---

### Violations Not Mapped to Slides
**Problem**: All violations show "Slide 0" or "Unknown"

**Solution**:
- This happens when TokenFactory API is down
- Violations are still found
- Just not mapped to specific slides
- Wait for API to return

---

## 🚀 Getting Started

### Quick Start with New Features

```bash
# 1. Start backend (if not running)
cd new_approach/backend
python main.py

# 2. Start frontend (if not running)
cd new_approach/frontend
npm start

# 3. Open browser
http://localhost:3000

# 4. Try the new workflow!
```

### First Time Using Enhanced Features

1. **Upload** a test PowerPoint
2. **Preview** the slides
3. **Select** just "Structure" module
4. **Run** the check
5. **Navigate** through slides
6. **Review** violations by slide

---

## 📚 Additional Resources

- **QUICKSTART.md** - Basic setup
- **FRONTEND_GUIDE.md** - UI details
- **ARCHITECTURE.md** - System design
- **TROUBLESHOOTING.md** - Common issues

---

**Enjoy the enhanced compliance checking experience! 🎉**
