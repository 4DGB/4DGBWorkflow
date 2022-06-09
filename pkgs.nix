#
# Nix derivations for Workflow
#
{ pkgs }:
  # 'pkgs' is expected to be overlayed with packages from submodules (see flake.nix)

let
  # Workflow source files
  workflow-src = pkgs.linkFarm "workflow-src" [
    { name = "workflow.py"; path = ./scripts/workflow.py; }
    { name = "project_template.json"; path = ./scripts/project_template.json; }
    { name = "csv2tracks"; path = ./scripts/csv2tracks; }
  ];

  # Workflow script
  workflow-build = { python3, db_pop, hic2structure }: pkgs.writeShellScriptBin "4dgb-workflow-build" (
    let
      py = python3.withPackages (p: with p; [pyyaml pandas hic2structure]);
      src = workflow-src;
    in ''
      export PATH="${db_pop}/bin:$PATH"
      ${py}/bin/python3 ${src}/workflow.py "$@"
    ''
  );
in 
{
  workflow-build = pkgs.callPackage workflow-build {};
}
