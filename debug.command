
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR
. ./blendenv.sh
$BLENDER_DIR/blender -P scripts/__debug__.py "blend/audiosculpture-rig - frames+glow.blend"
