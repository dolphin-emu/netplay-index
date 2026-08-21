{
  description = "Dolphin's NetPlay Index / Lobby Server";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

  inputs.uv2nix.url = "github:pyproject-nix/uv2nix";
  inputs.uv2nix.inputs.nixpkgs.follows = "nixpkgs";
  inputs.uv2nix.inputs.pyproject-nix.follows = "pyproject-nix";

  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";

  inputs.pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";
  inputs.pyproject-build-systems.inputs.nixpkgs.follows = "nixpkgs";
  inputs.pyproject-build-systems.inputs.pyproject-nix.follows = "pyproject-nix";

  outputs = { self, nixpkgs, flake-utils, uv2nix, pyproject-nix, pyproject-build-systems }:
  let
    perSystem = flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
        overlay = workspace.mkPyprojectOverlay {
          sourcePreference = "wheel";
        };
        python = pkgs.python313;
        pythonSet =
          (pkgs.callPackage pyproject-nix.build.packages { inherit python; })
          .overrideScope (pkgs.lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
          ]);
        venv = pythonSet.mkVirtualEnv "netplay-index-env" workspace.deps.default;
      in {
        packages.netplay-index = venv;
        packages.default = venv;

        apps.default = {
          type = "app";
          program = "${venv}/bin/netplay-index";
        };

        devShells.default = with pkgs; mkShell {
          packages = [ uv ];
        };
      });
  in
    perSystem // {
      overlays.default = final: prev: {
        netplay-index = self.packages.${final.system}.netplay-index;
      };
      overlay = self.overlays.default;
    };
}
