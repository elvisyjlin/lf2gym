#!/usr/bin/bash

function copy {
    md5_1=($(md5sum $1))
    md5_2=($(md5sum $2))
    if [ $md5_1 != $md5_2 ]; then
        cp -v $1 $2
    else
        echo "'$2' is up-to-date."
    fi
}

echo "Checking LF2 files..."
if [ ! -d F.LF ]; then
    echo "F.LF/ does not exist, cloning one from Github..."
    git clone https://github.com/Project-F/F.LF.git
fi
pushd F.LF
if [ ! -d LF2_19 ]; then
    echo "F.LF/LF2_19 does not exist, cloning one from Github..."
    git clone https://github.com/Project-F/LF2_19.git
fi
popd

echo "Replacing modified files..."
FROM="modify"
copy    $FROM/controller.js       F.LF/core/controller.js
copy    $FROM/game.html           F.LF/game/game.html
copy    $FROM/game.js             F.LF/game/game.js
copy    $FROM/global.js           F.LF/LF/global.js
copy    $FROM/character.js        F.LF/LF/character.js
copy    $FROM/match.js            F.LF/LF/match.js
copy    $FROM/weapon.js           F.LF/LF/weapon.js
copy    $FROM/background.js       F.LF/LF/background.js
copy    $FROM/back3.png           F.LF/LF2_19/bg/hkc/back3.png
copy    $FROM/message_overlay.png F.LF/LF2_19/UI/message_overlay.png
copy    $FROM/bg.js               F.LF/LF2_19/bg/hkc/bg.js
