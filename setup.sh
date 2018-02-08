#!/usr/bin/bash

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
cp -v   $FROM/controller.js       F.LF/core/controller.js
cp -v   $FROM/game.html           F.LF/game/game.html
cp -v   $FROM/game.js             F.LF/game/game.js
cp -v   $FROM/global.js           F.LF/LF/global.js
cp -v   $FROM/character.js        F.LF/LF/character.js
cp -v   $FROM/match.js            F.LF/LF/match.js
cp -v   $FROM/weapon.js           F.LF/LF/weapon.js
cp -v   $FROM/background.js       F.LF/LF/background.js
cp -v   $FROM/back3.png           F.LF/LF2_19/bg/hkc/back3.png
cp -v   $FROM/message_overlay.png F.LF/LF2_19/UI/message_overlay.png
cp -v   $FROM/bg.js               F.LF/LF2_19/bg/hkc/bg.js
