find */ -name "optimized_classifier.xml" | while IFS= read -r NAME; do NAME2=${NAME// /_}; cp -v "$NAME"  "/tmp/separate/${NAME2//\//_}"; done
