{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    nix-index-database.url = "github:nix-community/nix-index-database";
    nix-index-database.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, nix-index-database, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        packages = {
          default = pkgs.python3Packages.buildPythonPackage {
            pname = "apm";
            version = "0.1.0";
            src = ./.;
            format = "setuptools";
          };
        };
        devShells = {
          default = pkgs.mkShell {
            packages = [
              pkgs.python3
              pkgs.python3Packages.pip
              pkgs.python3Packages.setuptools
              nix-index-database.packages.${system}.default
            ];
          };
        };
      }
    );
}
