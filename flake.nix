# https://pyproject-nix.github.io/pyproject.nix/use-cases/pyproject.html
{
  description = "A basic flake using pyproject.toml project metadata";

  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs =
    { nixpkgs, pyproject-nix, ... }:
    let
      # This example is only using aarch64-darwin
      pkgs = nixpkgs.legacyPackages.aarch64-darwin;

      # pyfluidsynth = let
      #   pname = "pyfluidsynth";
      #   version = "1.3.4";
      #   pyproject = true;
      #   dependencies = [
      #     pkgs.python3Packages.setuptools
      #     pkgs.python3Packages.numpy
      #     pkgs.fluidsynth
      #   ];
      # in
      #   pkgs.python3Packages.buildPythonPackage {
      #     inherit pname version pyproject dependencies;
      #     src = pkgs.fetchPypi {
      #       inherit pname version;
      #       sha256 = "sha256-ynQcJity5IljFJxzv4roDkXITCPJvfgDomujJMuy1bI=";
      #     };
      #     doCheck = false;
      #   };

      # numpy1 = let
      #   pname = "numpy";
      #   version = "1.26.4";
      #   pyproject = true;
      # in
      #   pkgs.python3Packages.buildPythonPackage {
      #     inherit pname version pyproject;
      #     build-system = [
      #       pkgs.meson
      #     ];
      #     dependencies = [
      #       pkgs.python3Packages.cython
      #       pkgs.meson
      #     ];
      #     src = pkgs.fetchPypi {
      #       inherit pname version;
      #       sha256 = "sha256-KgKrqe0S5KxOs+qUIcQgMBoMZGDZgw10qd+H76SRIBA=";
      #     };
      #     doCheck = false;
      #   };

      # poisson-disc = let
      #   pname = "poisson_disc";
      #   version = "0.2.1";
      #   pyproject = true;
      # in
      #   pkgs.python3Packages.buildPythonPackage {
      #     inherit pname version pyproject;
      #     build-system = [
      #       pkgs.python3Packages.poetry-core
      #     ];
      #     dependencies = [
      #       pkgs.python3Packages.poetry-core
      #       numpy1
      #     ];
      #     src = pkgs.fetchPypi {
      #       inherit pname version;
      #       sha256 = "sha256-zicRLqvxu/OtGyihUAXTG//49FOQvN/SD4rgrOrisLQ=";
      #     };
      #     doCheck = false;
      #   };

      # pypi packages not provided in nixpkgs
      mingus = let
        pname = "mingus";
        version = "0.6.1";
        pyproject = true;
        dependencies = [
          pkgs.python3Packages.setuptools
          pkgs.python3Packages.six
          pkgs.python3Packages.numpy
          pkgs.fluidsynth
        ];
      in
        pkgs.python3Packages.buildPythonPackage {
          inherit pname version pyproject dependencies;

          # Wherever python's find_library looks, it's not in nix stores.
          # Patch to point mingus directly at the nix fluidsynth.
          # This is apparently a tried and tested nix python kludge:
          # https://github.com/search?q=repo%3ANixOS%2Fnixpkgs+ctypes.util.find_library&type=code
          postPatch = ''
              substituteInPlace "mingus/midi/pyfluidsynth.py" \
                --replace-fail 'find_library("fluidsynth")' "'${pkgs.fluidsynth}/lib/libfluidsynth.dylib'"
          '';

          src = pkgs.fetchPypi {
            inherit pname version;
            sha256 = "sha256-hcoiRp9bB1hYW7xc2BYrvk2gSc4315wUQ3ipIr6frwU=";
          };
          doCheck = false;
        };

      # Loads pyproject.toml into a high-level project representation
      # Do you notice how this is not tied to any `system` attribute or package sets?
      # That is because `project` refers to a pure data representation.
      project = pyproject-nix.lib.project.loadPyproject {
        # Read & unmarshal pyproject.toml relative to this project root.
        # projectRoot is also used to set `src` for renderers such as buildPythonPackage.
        projectRoot = ./.;
      };
      projectMetadata = project.pyproject.project;

      editablePackage = pkgs.python3.pkgs.mkPythonEditablePackage {
        pname = projectMetadata.name;
        inherit (projectMetadata) version scripts;
        root = "$PWD/src";
      };

      # We are using the default nixpkgs Python3 interpreter & package set.
      #
      # This means that you are purposefully ignoring:
      # - Version bounds
      # - Dependency sources (meaning local path dependencies won't resolve to the local path)
      #
      # To use packages from local sources see "Overriding Python packages" in the nixpkgs manual:
      # https://nixos.org/manual/nixpkgs/stable/#reference
      #
      # Or use an overlay generator such as uv2nix:
      # https://github.com/pyproject-nix/uv2nix
      python = pkgs.python3.override {
        packageOverrides = self: super: {
          ruff = pkgs.ruff;
          mypy = pkgs.python3Packages.mypy;
          python-lsp-server = pkgs.python3Packages.python-lsp-server;
          pylsp-mypy = pkgs.python3Packages.pylsp-mypy;
          mingus = mingus;
          # poisson-disc = poisson-disc;
        };
      };
    in
    {
      # Create a development shell containing dependencies from `pyproject.toml`
      devShells.aarch64-darwin.default =
        let
          # Returns a function that can be passed to `python.withPackages`
          arg = project.renderers.withPackages
            {
              inherit python;
              # Install the editable package to make its scripts available
              extraPackages = (ps: [ editablePackage ]);
              extras = [ "dev" "test" ];
            };

          # Returns a wrapped environment (virtualenv like) with all our packages
          pythonEnv = python.withPackages arg;

        in
        # Create a devShell like normal.
          pkgs.mkShell {
            packages = [
              pythonEnv
              pkgs.ruff
              pkgs.python3Packages.mypy
              pkgs.python3Packages.python-lsp-server
              pkgs.python3Packages.pylsp-mypy
              pkgs.python3Packages.ipython
            ];
          };

      # Build our package using `buildPythonPackage
      packages.aarch64-darwin.default =
        let
          # Returns an attribute set that can be passed to `buildPythonPackage`.
          attrs = project.renderers.buildPythonPackage { inherit python; };
        in
        # Pass attributes to buildPythonPackage.
        # Here is a good spot to add on any missing or custom attributes.
        python.pkgs.buildPythonApplication (attrs // {
          env.CUSTOM_ENVVAR = "hello";
        });
    };
}
