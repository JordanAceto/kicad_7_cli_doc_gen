# Documentation Generator for KiCad 7 Projects

## NOTE: holmesrichards maintains a [much more polished fork](https://gitlab.com/rsholmes/kdocgen) of this script 
- It implements several of the improvements proposed below and adds some nice multi-board-project behavior
- This version is left as-is for now as a basic example of how to use the KiCad 7 `kicad-cli`

## What it is:
- With the introduction of the `kicad-cli` tool in KiCad 7 we can now easily generate many outputs from the command line
- This is a quick and dirty python script that spits out documentation according to my own personal directory structure preference
- It's for Linux operating systems
- It intended as a standalone script, you **don't** need to run this from within the KiCad python terminal
- I imagine it will change and improve over time, this is just a quicky first pass to jot down some ideas, a starting point

## What it produces:
- Schematic PDF
- Interactive HTML BOM
- Basic CSV BOM
- Compressed gerbers and drill files
- PCB layers as PDFs
- Front and back of PCB as SVG
- STEP file of PCB
- If there is no README file for the project directory a simple README is generated

## Dependencies:
- [Interactive HTML BOM](https://github.com/openscopeproject/InteractiveHtmlBom)
  - Must be installed if you want to use it
  - make a symlink to `/usr/local/bin` so we can easily run it from the cli

## Improvements:
- User choice for the outputs
  - Maybe you could feed it some kind of structured JSON/YAML file with your preferences or something
- Detect the PCB stackup and generate the correct layers
- I like to make decorative panels out of PCB material
  - If the project is a panel, adjust the ouputs accordingly (don't need to plot a schematic for a panel, etc)
- There is some bug with the STEP output. It fails to rename the temporary file. The script manually renames it now
- The CSV BOM just runs one of the built in KiCad 7 BOM scripts, this could surely be tweaked for a more personal touch
- The schematic PDF does not use the user's color theme and fonts.
  - The `kicad-cli` help says that it will default to the schematic settings, but it doesn't seem to yet
- It doesn't do any error handling or checking yet
- We could come up with a nicer way of building the command line string for the outputs

## Example:
- Included is an example board which shows the intended project structure
- To get back to a baseline, delete the `docs` directory and `README.md` file in the example
- To generate docs for the example:
  - From the root of this directory `$python kicad_7_doc_gen.py example_board/`
  - Browse the newly generated `docs` directory and `README.me` file
