{
  description = "CUDA development environment for models from scratch";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python314;
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ python pkgs.uv pkgs.gcc ];

        # PyTorch wheels supply CUDA userspace libraries, but not the host driver.
        LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib pkgs.zlib ]}:/run/opengl-driver/lib";
        # Skip Triton's hardcoded /sbin/ldconfig lookup on NixOS.
        TRITON_LIBCUDA_PATH = "/run/opengl-driver/lib";

        # Triton builds Python extensions when compilation is enabled.
        CPATH = "${python}/include/python${python.pythonVersion}";
        UV_PYTHON = "${python}/bin/python${python.pythonVersion}";
        UV_PYTHON_DOWNLOADS = "never";
      };
    };
}
