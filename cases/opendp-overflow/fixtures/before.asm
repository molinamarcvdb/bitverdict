
compiled image:	file format mach-o arm64

Disassembly of section __TEXT,__text:

0000000100001694 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8>:
100001694: f9400829    	ldr	x9, [x1, #0x10]
100001698: b40000e9    	cbz	x9, 0x1000016b4 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0x20>
10000169c: f940042a    	ldr	x10, [x1, #0x8]
1000016a0: f100113f    	cmp	x9, #0x4
1000016a4: 54000122    	b.hs	0x1000016c8 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0x34>
1000016a8: d280000b    	mov	x11, #0x0               ; =0
1000016ac: 5280000c    	mov	w12, #0x0               ; =0
1000016b0: 14000031    	b	0x100001774 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0xe0>
1000016b4: 5280000c    	mov	w12, #0x0               ; =0
1000016b8: b900090c    	str	w12, [x8, #0x8]
1000016bc: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
1000016c0: f9000109    	str	x9, [x8]
1000016c4: d65f03c0    	ret
1000016c8: f100413f    	cmp	x9, #0x10
1000016cc: 54000082    	b.hs	0x1000016dc <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0x48>
1000016d0: d280000b    	mov	x11, #0x0               ; =0
1000016d4: 5280000c    	mov	w12, #0x0               ; =0
1000016d8: 14000019    	b	0x10000173c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0xa8>
1000016dc: 927ced2b    	and	x11, x9, #0xfffffffffffffff0
1000016e0: 9100814c    	add	x12, x10, #0x20
1000016e4: 6f00e400    	movi.2d	v0, #0000000000000000
1000016e8: aa0b03ed    	mov	x13, x11
1000016ec: 6f00e401    	movi.2d	v1, #0000000000000000
1000016f0: 6f00e402    	movi.2d	v2, #0000000000000000
1000016f4: 6f00e403    	movi.2d	v3, #0000000000000000
1000016f8: ad7f1584    	ldp	q4, q5, [x12, #-0x20]
1000016fc: acc21d86    	ldp	q6, q7, [x12], #0x40
100001700: 4ea08480    	add.4s	v0, v4, v0
100001704: 4ea184a1    	add.4s	v1, v5, v1
100001708: 4ea284c2    	add.4s	v2, v6, v2
10000170c: 4ea384e3    	add.4s	v3, v7, v3
100001710: f10041ad    	subs	x13, x13, #0x10
100001714: 54ffff21    	b.ne	0x1000016f8 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0x64>
100001718: 4ea08420    	add.4s	v0, v1, v0
10000171c: 4ea08440    	add.4s	v0, v2, v0
100001720: 4ea08460    	add.4s	v0, v3, v0
100001724: 4eb1b800    	addv.4s	s0, v0
100001728: 1e26000c    	fmov	w12, s0
10000172c: eb0b013f    	cmp	x9, x11
100001730: 540002e0    	b.eq	0x10000178c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0xf8>
100001734: f27e053f    	tst	x9, #0xc
100001738: 540001e0    	b.eq	0x100001774 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0xe0>
10000173c: aa0b03ed    	mov	x13, x11
100001740: 927ef52b    	and	x11, x9, #0xfffffffffffffffc
100001744: 6f00e400    	movi.2d	v0, #0000000000000000
100001748: 4e041d80    	mov.s	v0[0], w12
10000174c: cb0b01ac    	sub	x12, x13, x11
100001750: 8b0d094d    	add	x13, x10, x13, lsl #2
100001754: 3cc105a1    	ldr	q1, [x13], #0x10
100001758: 4ea08420    	add.4s	v0, v1, v0
10000175c: b100118c    	adds	x12, x12, #0x4
100001760: 54ffffa1    	b.ne	0x100001754 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0xc0>
100001764: 4eb1b800    	addv.4s	s0, v0
100001768: 1e26000c    	fmov	w12, s0
10000176c: eb0b013f    	cmp	x9, x11
100001770: 540000e0    	b.eq	0x10000178c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0xf8>
100001774: cb0b0129    	sub	x9, x9, x11
100001778: 8b0b094a    	add	x10, x10, x11, lsl #2
10000177c: b840454b    	ldr	w11, [x10], #0x4
100001780: 0b0c016c    	add	w12, w11, w12
100001784: f1000529    	subs	x9, x9, #0x1
100001788: 54ffffa1    	b.ne	0x10000177c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::h3f8228636e97aba8+0xe8>
10000178c: b900090c    	str	w12, [x8, #0x8]
100001790: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
100001794: f9000109    	str	x9, [x8]
100001798: d65f03c0    	ret
