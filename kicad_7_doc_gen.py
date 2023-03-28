#!/usr/bin/python3

import argparse
import fnmatch
import os


parser = argparse.ArgumentParser()

parser.add_argument(
    'project_dir',
    type=str,
    help='path to directory with KiCad 7 project'
)

args = parser.parse_args()

proj_dir = args.project_dir


def find_file(pattern: str, path: str) -> str:
    """`find_file(pat, path)` is the first file found matching pattern `pat`."""
    for root, _, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)


def get_project_name(path: str) -> str:
    """`get_project_name(path)` is the name of the KiCad 7 project in the given path."""
    project_file = find_file("*.kicad_pro", path)
    project_name = project_file.split(".kicad_pro")[0]
    project_name = project_name.split("/")[-1]
    return project_name


# TODO this is just a naive list of the default layers, there should be some way to select only desired layers and to
# use the right names if the user renamed any layers
pcb_layers = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu", "F.SilkS", "B.SilkS",
              "F.Paste", "B.Paste", "F.Mask", "B.Mask", "Edge.Cuts"]


class KiCad7Proj():
    def __init__(self, path: str, layers: list[str]):
        self.proj_dir = path
        self.proj_name = get_project_name(path)
        self.sch_file = find_file(self.proj_name+".kicad_sch", path)
        self.pcb_file = find_file(self.proj_name+".kicad_pcb", path)
        self.layers = layers


k7_proj = KiCad7Proj(proj_dir, pcb_layers)


def make_dir_structure(k7_proj: KiCad7Proj) -> None:
    # make sure that the expected directory structure is in place
    base_dir = f"{k7_proj.proj_dir}docs"
    dirs = ["2D", "3D", "BOM"]

    if not os.path.exists(base_dir):
        os.system(f"mkdir {base_dir}")

    for dir in dirs:
        if not os.path.exists(f"{base_dir}/{dir}"):
            os.system(f"mkdir {base_dir}/{dir}")


def schem_pdf(k7_proj: KiCad7Proj) -> None:
    # TODO default color and fonts are used, I want it to plot the user theme/fonts
    os.system(
        f"kicad-cli sch export pdf -o {k7_proj.proj_dir}/docs/{k7_proj.proj_name}_schematic.pdf {k7_proj.sch_file}")


def pcb_2D_layers(k7_proj: KiCad7Proj) -> None:
    # PCB front and back as SVGs
    os.system(
        f"kicad-cli pcb export svg --page-size-mode 2 --exclude-drawing-sheet --layers Edge.Cuts,F.SilkS,F.Cu -o {k7_proj.proj_dir}docs/2D/{k7_proj.proj_name}_front.svg {k7_proj.pcb_file}")
    os.system(
        f"kicad-cli pcb export svg --page-size-mode 2 --exclude-drawing-sheet --mirror --layers Edge.Cuts,B.SilkS,B.Cu -o {k7_proj.proj_dir}docs/2D/{k7_proj.proj_name}_back.svg {k7_proj.pcb_file}")
    # all the board layers as individual PDFs
    for layer in k7_proj.layers:
        os.system(
            f"kicad-cli pcb export pdf --black-and-white --exclude-value --exclude-refdes --include-border-title --layers {layer} -o {k7_proj.proj_dir}docs/2D/{k7_proj.proj_name}_{layer}.pdf {k7_proj.pcb_file}")


def csv_bom(k7_proj: KiCad7Proj) -> None:
    # first make the netlist
    os.system(
        f"kicad-cli sch export netlist --format kicadxml -o {k7_proj.proj_dir}/docs/BOM/{k7_proj.proj_name}_netlist.xml {k7_proj.sch_file}")
    # runs one of the basic BOM scripts, TODO could/should get fancier with this
    os.system(
        f"/usr/bin/python3 /usr/share/kicad/plugins/bom_csv_grouped_extra.py {k7_proj.proj_dir}docs/BOM/{k7_proj.proj_name}_netlist.xml {k7_proj.proj_dir}docs/BOM/{k7_proj.proj_name}_BOM.csv")
    # delete the netlist
    os.system(f"rm {k7_proj.proj_dir}docs/BOM/{k7_proj.proj_name}_netlist.xml")


def ibom(k7_proj: KiCad7Proj) -> None:
    # note the symlink to the ibom generator in `usr/local/bin`, if you put it somewhere else you may need to mess with this
    os.system(
        f"/usr/bin/python3 /usr/local/bin/generate_interactive_bom.py --dark-mode --no-browser --dest-dir ../docs/BOM/ --name-format {k7_proj.proj_name}_ibom {k7_proj.pcb_file}")


def gerbers(k7_proj: KiCad7Proj) -> None:
    layers_as_str = ",".join(k7_proj.layers)
    temp_dir = f"{k7_proj.proj_dir}temp/"
    os.system(f"mkdir {temp_dir}")
    # gerbers
    os.system(
        f"kicad-cli pcb export gerbers --layers {layers_as_str} -o {temp_dir} {k7_proj.pcb_file}")
    # drill files
    os.system(
        f"kicad-cli pcb export drill --units mm --generate-map --map-format gerberx2 -o {temp_dir} {k7_proj.pcb_file}")
    # zip em up
    os.system(
        f"zip -j {k7_proj.proj_dir}docs/{k7_proj.proj_name}_gerbers.zip {temp_dir}*")
    os.system(f"rm -r {temp_dir}")


def step(k7_proj: KiCad7Proj) -> None:
    os.system(
        f"kicad-cli pcb export step --force --subst-models -o {k7_proj.proj_dir}docs/3D/ {k7_proj.pcb_file}")
    # hack, TODO find out why the .step file is not automatically renamed
    print("** manually renaming STEP file **")
    os.system(
        f"mv {proj_dir}docs/3D/*.step {proj_dir}docs/3D/{k7_proj.proj_name}.step ")


def readme(k7_proj: KiCad7Proj) -> None:
    # make a basic README with the project name and front/back PCB view if there is no existing README
    readme_exists = any([os.path.isfile(f"{k7_proj.proj_dir}README.md"), os.path.isfile(
        f"{k7_proj.proj_dir}Readme.md"), os.path.isfile(f"{k7_proj.proj_dir}readme.md")])

    if not readme_exists:
        print("Generating basic README file")
        f = open(f"{k7_proj.proj_dir}README.md", "w")
        f.write(f"# {k7_proj.proj_name}\n\n")
        f.write(f"![PCB front](./docs/2D/{k7_proj.proj_name}_front.svg)\n")
        f.write(f"![PCB back](./docs/2D/{k7_proj.proj_name}_back.svg)\n")
        f.close()
    else:
        print("README already exists, skipping README")


# generate the outputs
make_dir_structure(k7_proj)
schem_pdf(k7_proj)
pcb_2D_layers(k7_proj)
ibom(k7_proj)
csv_bom(k7_proj)
gerbers(k7_proj)
step(k7_proj)
readme(k7_proj)
