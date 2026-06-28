#!/bin/bash

# Woddy WOD and Program Generation Pipeline
# Generates all programs and WODs needed for the app

set -e  # Exit on error

# Load environment
source venv/bin/activate
# ANTHROPIC_API_KEY should be set in your environment (.env or shell config)
# Do not commit secrets to git!

echo "🏋️  Woddy Generation Pipeline"
echo "=============================="
echo ""

# Programs
echo "📋 PROGRAMS (2 variants)"
echo ""
python3 scripts/generate.py --type program --name back-in-shape --weeks 2
echo "✅ 2-week program generated"
echo ""

python3 scripts/generate.py --type program --name back-in-shape --weeks 3
echo "✅ 3-week program generated"
echo ""

# WODs
echo "💪 WODS (5 per category)"
echo ""

echo "Generating full-body WODs..."
python3 scripts/generate.py --type wod --count 5 --category full-body
echo "✅ Full-body WODs generated"
echo ""

echo "Generating upper-body WODs..."
python3 scripts/generate.py --type wod --count 5 --category upper-body
echo "✅ Upper-body WODs generated"
echo ""

echo "Generating lower-body WODs..."
python3 scripts/generate.py --type wod --count 5 --category lower-body
echo "✅ Lower-body WODs generated"
echo ""

echo "Generating strength WODs..."
python3 scripts/generate.py --type wod --count 5 --category strength
echo "✅ Strength WODs generated"
echo ""

echo "Generating cardio WODs..."
python3 scripts/generate.py --type wod --count 5 --category cardio
echo "✅ Cardio WODs generated"
echo ""

echo "=============================="
echo "🎉 All generations complete!"
echo ""
echo "📊 Generated files:"
ls -lh output/*.json | awk '{print "  " $9 " (" $5 ")"}'
