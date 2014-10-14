all: anakin.png dec-anakin-original.png

anakin.png: eocd2_payload-similar.apk
	python encrypt-apk.py
	mv dec-anakin-original.png anakin.png
	@echo "-> please add anakin.png to your wrapping APK"

eocd2_payload-similar.apk: anakin-original.png payload.apk encrypt-apk.py axdupe_eocd.py
	@echo "add EOCD and padding -----"
	python axdupe_eocd.py payload-similar.apk
        # padding the APK. TODO: make sure multiple of 16
	echo -n "123456789" >> eocd2_payload-similar.apk
        # now eocd2_payload-similar.apk is a valid zip
        # update encrypt-apk script
	sed --in-place 's/payload-similar/eocd2_payload-similar/g' encrypt-apk.py

encrypt-apk.py: anakin-original.png payload.apk
	@echo "make similar APK that encrypts as PNG -----"
	python angecrypt.py payload.apk anakin-original.png payload-similar.apk 'Anakin= DarkSide' aes > encrypt-apk.py

payload.apk: 
        # copy APK from its directory
	cp ../payload/bin/PayloadPoC-release.apk payload.apk

dec-anakin-original.png: decrypt-png.py
        # decrypt PNG -> APK
	python decrypt-png.py

decrypt-png.py: encrypt-apk.py
        # make decrypt script
	sed -e 's/eocd2_payload-similar\.apk/anakin\.png/g' -e 's/encrypt/decrypt/g' < encrypt-apk.py > tmp
	mv tmp decrypt-png.py

clean:
	rm -f payload-similar.apk 
	rm -f payload.apk
	rm -f eocd2_payload-similar.apk
	rm -f dec-anakin-original.png
	rm -f tmp
	rm -f encrypt-apk.py
	rm -f anakin.png
	rm -f decrypt-png.py
