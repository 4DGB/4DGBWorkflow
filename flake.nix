#
# Nix flake for 4DGB Workflow
# 
# This flake brings in the flakes exported by both submodules, provides
# a development environment with the submodules' packages available and
# exports the workflow.py script as a package (called '4dgb-workflow-build')
#
{
  description = "Python module for processing Hi-C files through LAMMPS";

  inputs = {
    # Nixpkgs
    nixpkgs.url = "github:NixOS/nixpkgs/release-22.05";

    # hic2structure python package
    hic.url = "./submodules/3DStructure";

    # 4DGB Browser
    browser.url = "./submodules/4DGB";

    # Flake-compat library
    # (Used to generate a flake-less nix.shell file)
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };

    # Flake-utils library
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-compat, flake-utils, hic, browser }:
    flake-utils.lib.eachDefaultSystem (system:
      with builtins;
      let
        # Install packages from submodules as overlays
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            # hic2strucure
            (self: super: with hic.packages.${system}; {
              inherit lammps;
              hic2structure = hic2structure.override { python3 = super.python310; };
            })
            # Browser
            (self: super: with browser.packages.${system}; {
              gtkserver = gtkserver.override { python3 = super.python310; };
              db_pop = db_pop.override { python3 = super.python310; };
            })
          ];
        };

        myPkgs = import ./pkgs.nix { inherit pkgs; };
      in
      with pkgs;
      rec {
        packages = {
          workflow-build = myPkgs.workflow-build.override { python3 = python310; };
        };

        # Development environment
        devShell = mkShell {
          buildInputs = [
            (python310.withPackages (p: with p; [pyyaml pandas]))
            lammps hic2structure
            gtkserver db_pop
          ];
        };
      }
    );
}
