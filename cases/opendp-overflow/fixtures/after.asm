
compiled image:	file format mach-o arm64

Disassembly of section __TEXT,__text:

000000010000160c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h14db8bedc4567392>:
10000160c: f9400829    	ldr	x9, [x1, #0x10]
100001610: b40001c9    	cbz	x9, 0x100001648 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h14db8bedc4567392+0x3c>
100001614: 5280000a    	mov	w10, #0x0               ; =0
100001618: f940042b    	ldr	x11, [x1, #0x8]
10000161c: b840456c    	ldr	w12, [x11], #0x4
100001620: 2b0c014a    	adds	w10, w10, w12
100001624: 131f7d4c    	asr	w12, w10, #31
100001628: 5201018c    	eor	w12, w12, #0x80000000
10000162c: 1a8a618a    	csel	w10, w12, w10, vs
100001630: f1000529    	subs	x9, x9, #0x1
100001634: 54ffff41    	b.ne	0x10000161c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h14db8bedc4567392+0x10>
100001638: b900090a    	str	w10, [x8, #0x8]
10000163c: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
100001640: f9000109    	str	x9, [x8]
100001644: d65f03c0    	ret
100001648: 5280000a    	mov	w10, #0x0               ; =0
10000164c: b900090a    	str	w10, [x8, #0x8]
100001650: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
100001654: f9000109    	str	x9, [x8]
100001658: d65f03c0    	ret
