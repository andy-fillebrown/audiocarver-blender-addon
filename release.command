
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR
. ./blendenv.sh
$BLENDER_DIR/blender -b blend/audiosculpture-rig.blend -P src/testing/test.py
