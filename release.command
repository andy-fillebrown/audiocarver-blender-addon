
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR
. ./blendenv.sh
$BLENDER_DIR/blender blend/audiosculpture-rig.blend
