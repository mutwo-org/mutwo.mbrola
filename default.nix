with import <nixpkgs> {};
with pkgs.python3Packages;

let

  mutwo-core-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.core/archive/97aea97f996973955889630c437ceaea405ea0a7.tar.gz";
  mutwo-core = import (mutwo-core-archive + "/default.nix");

  mutwo-music-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.music/archive/4e4369c1c9bb599f47ec65eb86f87e9179e17d97.tar.gz";
  mutwo-music = import (mutwo-music-archive + "/default.nix");

  voxpopuli = pkgs.python39Packages.buildPythonPackage rec {
    name = "voxpopuli";

    # FIXME

    # Because of this code voxpopuli can't find mbrola voices in Nix:
    # https://github.com/hadware/voxpopuli/blob/master/voxpopuli/main.py#L68-L71
    # I should open a MR to make this possible.
    # A quick fix is to simply write:

    # >>> import voxpopuli
    # >>> import shutil
    # >>> mbrola_binary_path = shutil.which("mbrola")
    # >>> voxpopuli.Voice.mbrola_voices_folder = "/".join(mbrola_binary_path.split('/')[:-2]) + "/share/mbrola/voices/"

    doCheck = false;
    src = fetchFromGitHub {
      owner = "hadware";
      repo = name;
      rev = "fb94a6130c046bb9f7a27aaaed2a4b434666faa9";
      sha256 = "sha256-RYV/Oj7bLPFuYkOI22vzDCFNIrtP14k6rylicJeWTNY=";
    };
    propagatedBuildInputs = [
      mbrola
      espeak-classic
      python39Packages.nose
    ];
  };


in

  buildPythonPackage rec {
    name = "mutwo.mbrola";
    src = fetchFromGitHub {
      owner = "mutwo-org";
      repo = name;
      rev = "f449a5be950e305894df43d8b43e765175fac1f9";
      sha256 = "sha256-/vW49sOy0ngJaTSufJy9MPTKRxA7YDel5fnUsPZWp+8=";
    };
    propagatedBuildInputs = [
      mutwo-core
      mutwo-music
      voxpopuli
    ];
    doCheck = false;
  }
