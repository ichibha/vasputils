send:
	rsync -av --exclude=".*" --exclude="__pycache__" ./ unimac1:/Volumes/work/admin/packages/vasputils/
