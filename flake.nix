{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
      forEachSystem = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      packages = forEachSystem (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.python3Packages.buildPythonPackage {
            pname = "apm";
            version = "0.1.0";
            src = ./.;
            format = "setuptools";
          };
        });

      devShells = forEachSystem (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.python3
              pkgs.python3Packages.pip
              pkgs.python3Packages.setuptools
            ];
            shellHook = ''
              pip install --e .
            '';
          };
        });
    };
}