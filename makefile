send:
	rsync -av --delete --exclude=".*" --exclude="__pycache__" ./ unimac1:/Volumes/work/admin/packages/vasputils/
	rsync -av --delete --exclude=".*" --exclude="__pycache__" ./ kagayaki:~/vasputils/
