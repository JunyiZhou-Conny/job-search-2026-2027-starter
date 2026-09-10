# Rendered Polar maps

These files are generated from the `.mmd` sources.

Open the SVG in a browser and zoom. The master poster is a wide landscape, six columns from control plane to workflow inventory.

Regenerate with:

```bash
python3 scripts/render_polar_system_map.py --png
```

The renderer wraps each SVG in HTML and uses Chrome plus WenQuanYi so Chinese labels stay readable.
