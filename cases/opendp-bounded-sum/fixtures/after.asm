
build/after/opendp-sum-probe:	file format mach-o arm64

Disassembly of section __TEXT,__text:

000000010000334c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57>:
10000334c: f9400829    	ldr	x9, [x1, #0x10]
100003350: b40000e9    	cbz	x9, 0x10000336c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0x20>
100003354: f940042a    	ldr	x10, [x1, #0x8]
100003358: f100113f    	cmp	x9, #0x4
10000335c: 54000122    	b.hs	0x100003380 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0x34>
100003360: d280000b    	mov	x11, #0x0               ; =0
100003364: 5280000c    	mov	w12, #0x0               ; =0
100003368: 14000031    	b	0x10000342c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0xe0>
10000336c: 5280000c    	mov	w12, #0x0               ; =0
100003370: b900090c    	str	w12, [x8, #0x8]
100003374: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
100003378: f9000109    	str	x9, [x8]
10000337c: d65f03c0    	ret
100003380: f100413f    	cmp	x9, #0x10
100003384: 54000082    	b.hs	0x100003394 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0x48>
100003388: d280000b    	mov	x11, #0x0               ; =0
10000338c: 5280000c    	mov	w12, #0x0               ; =0
100003390: 14000019    	b	0x1000033f4 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0xa8>
100003394: 927ced2b    	and	x11, x9, #0xfffffffffffffff0
100003398: 9100814c    	add	x12, x10, #0x20
10000339c: 6f00e400    	movi.2d	v0, #0000000000000000
1000033a0: aa0b03ed    	mov	x13, x11
1000033a4: 6f00e401    	movi.2d	v1, #0000000000000000
1000033a8: 6f00e402    	movi.2d	v2, #0000000000000000
1000033ac: 6f00e403    	movi.2d	v3, #0000000000000000
1000033b0: ad7f1584    	ldp	q4, q5, [x12, #-0x20]
1000033b4: acc21d86    	ldp	q6, q7, [x12], #0x40
1000033b8: 4ea08480    	add.4s	v0, v4, v0
1000033bc: 4ea184a1    	add.4s	v1, v5, v1
1000033c0: 4ea284c2    	add.4s	v2, v6, v2
1000033c4: 4ea384e3    	add.4s	v3, v7, v3
1000033c8: f10041ad    	subs	x13, x13, #0x10
1000033cc: 54ffff21    	b.ne	0x1000033b0 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0x64>
1000033d0: 4ea08420    	add.4s	v0, v1, v0
1000033d4: 4ea08440    	add.4s	v0, v2, v0
1000033d8: 4ea08460    	add.4s	v0, v3, v0
1000033dc: 4eb1b800    	addv.4s	s0, v0
1000033e0: 1e26000c    	fmov	w12, s0
1000033e4: eb0b013f    	cmp	x9, x11
1000033e8: 540002e0    	b.eq	0x100003444 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0xf8>
1000033ec: f27e053f    	tst	x9, #0xc
1000033f0: 540001e0    	b.eq	0x10000342c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0xe0>
1000033f4: aa0b03ed    	mov	x13, x11
1000033f8: 927ef52b    	and	x11, x9, #0xfffffffffffffffc
1000033fc: 6f00e400    	movi.2d	v0, #0000000000000000
100003400: 4e041d80    	mov.s	v0[0], w12
100003404: cb0b01ac    	sub	x12, x13, x11
100003408: 8b0d094d    	add	x13, x10, x13, lsl #2
10000340c: 3cc105a1    	ldr	q1, [x13], #0x10
100003410: 4ea08420    	add.4s	v0, v1, v0
100003414: b100118c    	adds	x12, x12, #0x4
100003418: 54ffffa1    	b.ne	0x10000340c <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0xc0>
10000341c: 4eb1b800    	addv.4s	s0, v0
100003420: 1e26000c    	fmov	w12, s0
100003424: eb0b013f    	cmp	x9, x11
100003428: 540000e0    	b.eq	0x100003444 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0xf8>
10000342c: cb0b0129    	sub	x9, x9, x11
100003430: 8b0b094a    	add	x10, x10, x11, lsl #2
100003434: b840454b    	ldr	w11, [x10], #0x4
100003438: 0b0c016c    	add	w12, w11, w12
10000343c: f1000529    	subs	x9, x9, #0x1
100003440: 54ffffa1    	b.ne	0x100003434 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::hd2fdd4fa65a0bc57+0xe8>
100003444: b900090c    	str	w12, [x8, #0x8]
100003448: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
10000344c: f9000109    	str	x9, [x8]
100003450: d65f03c0    	ret


build/after/opendp-sum-probe:	file format mach-o arm64

Disassembly of section __TEXT,__text:

000000010000351c <opendp::trans::sum::make_sized_bounded_sum::_$u7b$$u7b$closure$u7d$$u7d$::had94f1eaa3a509db>:
10000351c: d100c3ff    	sub	sp, sp, #0x30
100003520: a9014ff4    	stp	x20, x19, [sp, #0x10]
100003524: a9027bfd    	stp	x29, x30, [sp, #0x20]
100003528: 910083fd    	add	x29, sp, #0x20
10000352c: aa0003f3    	mov	x19, x0
100003530: aa0803f4    	mov	x20, x8
100003534: b9400028    	ldr	w8, [x1]
100003538: 53017d00    	lsr	w0, w8, #1
10000353c: aa1403e8    	mov	x8, x20
100003540: 94000188    	bl	0x100003b60 <_$LT$i32$u20$as$u20$opendp..traits..cast..InfCast$LT$u32$GT$$GT$::inf_cast::h2275253f3d50b82e>
100003544: f9400289    	ldr	x9, [x20]
100003548: b24107ea    	mov	x10, #-0x7fffffffffffffff ; =-9223372036854775807
10000354c: eb0a013f    	cmp	x9, x10
100003550: 540000e1    	b.ne	0x10000356c <opendp::trans::sum::make_sized_bounded_sum::_$u7b$$u7b$closure$u7d$$u7d$::had94f1eaa3a509db+0x50>
100003554: b9400a89    	ldr	w9, [x20, #0x8]
100003558: b9000fe9    	str	w9, [sp, #0xc]
10000355c: 910033e0    	add	x0, sp, #0xc
100003560: aa1403e8    	mov	x8, x20
100003564: aa1303e1    	mov	x1, x19
100003568: 940000e7    	bl	0x100003904 <_$LT$i32$u20$as$u20$opendp..traits..arithmetic..InfMul$GT$::inf_mul::h09adcb0335e7f1f3>
10000356c: a9427bfd    	ldp	x29, x30, [sp, #0x20]
100003570: a9414ff4    	ldp	x20, x19, [sp, #0x10]
100003574: 9100c3ff    	add	sp, sp, #0x30
100003578: d65f03c0    	ret


build/after/opendp-sum-probe:	file format mach-o arm64

Disassembly of section __TEXT,__text:

0000000100003b60 <_$LT$i32$u20$as$u20$opendp..traits..cast..InfCast$LT$u32$GT$$GT$::inf_cast::h2275253f3d50b82e>:
100003b60: 14000001    	b	0x100003b64 <_$LT$i32$u20$as$u20$opendp..traits..cast..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h08552a80f22a469e>


build/after/opendp-sum-probe:	file format mach-o arm64

Disassembly of section __TEXT,__text:

0000000100003b64 <_$LT$i32$u20$as$u20$opendp..traits..cast..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h08552a80f22a469e>:
100003b64: d10203ff    	sub	sp, sp, #0x80
100003b68: a90367fa    	stp	x26, x25, [sp, #0x30]
100003b6c: a9045ff8    	stp	x24, x23, [sp, #0x40]
100003b70: a90557f6    	stp	x22, x21, [sp, #0x50]
100003b74: a9064ff4    	stp	x20, x19, [sp, #0x60]
100003b78: a9077bfd    	stp	x29, x30, [sp, #0x70]
100003b7c: 9101c3fd    	add	x29, sp, #0x70
100003b80: 37f800a0    	tbnz	w0, #0x1f, 0x100003b94 <_$LT$i32$u20$as$u20$opendp..traits..cast..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h08552a80f22a469e+0x30>
100003b84: b9000900    	str	w0, [x8, #0x8]
100003b88: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
100003b8c: f9000109    	str	x9, [x8]
100003b90: 1400002d    	b	0x100003c44 <_$LT$i32$u20$as$u20$opendp..traits..cast..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h08552a80f22a469e+0xe0>
100003b94: aa0803f9    	mov	x25, x8
100003b98: 9100bfe8    	add	x8, sp, #0x2f
100003b9c: 90000009    	adrp	x9, 0x100003000 <core::ptr::drop_in_place$LT$opendp..error..Error$GT$::he1e7d775d12bf158+0x5c>
100003ba0: 91358129    	add	x9, x9, #0xd60
100003ba4: a901a7e8    	stp	x8, x9, [sp, #0x18]
100003ba8: b0000200    	adrp	x0, 0x100044000 <core::unicode::unicode_data::grapheme_extend::SHORT_OFFSET_RUNS::h068fceb00e1a42b2+0xbc>
100003bac: 911fe800    	add	x0, x0, #0x7fa
100003bb0: 910003e8    	mov	x8, sp
100003bb4: 910063e1    	add	x1, sp, #0x18
100003bb8: 9400cca9    	bl	0x100036e5c <alloc::fmt::format::format_inner::hd571df24e790cabc>
100003bbc: f9400bf3    	ldr	x19, [sp, #0x10]
100003bc0: b6f800b3    	tbz	x19, #0x3f, 0x100003bd4 <_$LT$i32$u20$as$u20$opendp..traits..cast..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h08552a80f22a469e+0x70>
100003bc4: d2800017    	mov	x23, #0x0               ; =0
100003bc8: aa1703e0    	mov	x0, x23
100003bcc: aa1303e1    	mov	x1, x19
100003bd0: 9400f270    	bl	0x100040590 <alloc::raw_vec::handle_error::hd9deaf7dc19ebb3f>
100003bd4: a94057f4    	ldp	x20, x21, [sp]
100003bd8: b4000133    	cbz	x19, 0x100003bfc <_$LT$i32$u20$as$u20$opendp..traits..cast..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h08552a80f22a469e+0x98>
100003bdc: 97ffff3f    	bl	0x1000038d8 <__rustc::__rust_no_alloc_shim_is_unstable_v2>
100003be0: 52800037    	mov	w23, #0x1               ; =1
100003be4: aa1303e0    	mov	x0, x19
100003be8: 52800021    	mov	w1, #0x1                ; =1
100003bec: 97ffff37    	bl	0x1000038c8 <__rustc::__rust_alloc>
100003bf0: b4fffec0    	cbz	x0, 0x100003bc8 <_$LT$i32$u20$as$u20$opendp..traits..cast..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h08552a80f22a469e+0x64>
100003bf4: aa0003f6    	mov	x22, x0
100003bf8: 14000002    	b	0x100003c00 <_$LT$i32$u20$as$u20$opendp..traits..cast..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h08552a80f22a469e+0x9c>
100003bfc: 52800036    	mov	w22, #0x1               ; =1
100003c00: aa1603e0    	mov	x0, x22
100003c04: aa1503e1    	mov	x1, x21
100003c08: aa1303e2    	mov	x2, x19
100003c0c: 9400f41e    	bl	0x100040c84 <dyld_stub_binder+0x100040c84>
100003c10: 94000349    	bl	0x100004934 <backtrace::capture::Backtrace::new_unresolved::h1fabcc9010bc1e2d>
100003c14: aa0003f7    	mov	x23, x0
100003c18: aa0103f8    	mov	x24, x1
100003c1c: b40000b4    	cbz	x20, 0x100003c30 <_$LT$i32$u20$as$u20$opendp..traits..cast..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h08552a80f22a469e+0xcc>
100003c20: aa1503e0    	mov	x0, x21
100003c24: aa1403e1    	mov	x1, x20
100003c28: 52800022    	mov	w2, #0x1                ; =1
100003c2c: 97ffff28    	bl	0x1000038cc <__rustc::__rust_dealloc>
100003c30: a9005b33    	stp	x19, x22, [x25]
100003c34: a9015f33    	stp	x19, x23, [x25, #0x10]
100003c38: f9001338    	str	x24, [x25, #0x20]
100003c3c: 528000a8    	mov	w8, #0x5                ; =5
100003c40: 3900a328    	strb	w8, [x25, #0x28]
100003c44: a9477bfd    	ldp	x29, x30, [sp, #0x70]
100003c48: a9464ff4    	ldp	x20, x19, [sp, #0x60]
100003c4c: a94557f6    	ldp	x22, x21, [sp, #0x50]
100003c50: a9445ff8    	ldp	x24, x23, [sp, #0x40]
100003c54: a94367fa    	ldp	x26, x25, [sp, #0x30]
100003c58: 910203ff    	add	sp, sp, #0x80
100003c5c: d65f03c0    	ret


build/after/opendp-sum-probe:	file format mach-o arm64

Disassembly of section __TEXT,__text:

0000000100003904 <_$LT$i32$u20$as$u20$opendp..traits..arithmetic..InfMul$GT$::inf_mul::h09adcb0335e7f1f3>:
100003904: d10083ff    	sub	sp, sp, #0x20
100003908: a9017bfd    	stp	x29, x30, [sp, #0x10]
10000390c: 910043fd    	add	x29, sp, #0x10
100003910: a90007e0    	stp	x0, x1, [sp]
100003914: b9800009    	ldrsw	x9, [x0]
100003918: b980002a    	ldrsw	x10, [x1]
10000391c: 9b2a7d29    	smull	x9, w9, w10
100003920: eb29c13f    	cmp	x9, w9, sxtw
100003924: 540000e1    	b.ne	0x100003940 <_$LT$i32$u20$as$u20$opendp..traits..arithmetic..InfMul$GT$::inf_mul::h09adcb0335e7f1f3+0x3c>
100003928: b9000909    	str	w9, [x8, #0x8]
10000392c: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
100003930: f9000109    	str	x9, [x8]
100003934: a9417bfd    	ldp	x29, x30, [sp, #0x10]
100003938: 910083ff    	add	sp, sp, #0x20
10000393c: d65f03c0    	ret
100003940: 910003e1    	mov	x1, sp
100003944: 910023e2    	add	x2, sp, #0x8
100003948: aa0803e0    	mov	x0, x8
10000394c: 94000019    	bl	0x1000039b0 <_$LT$i32$u20$as$u20$opendp..traits..arithmetic..AlertingMul$GT$::alerting_mul::_$u7b$$u7b$closure$u7d$$u7d$::h1a3011cbf0b94945>
100003950: a9417bfd    	ldp	x29, x30, [sp, #0x10]
100003954: 910083ff    	add	sp, sp, #0x20
100003958: d65f03c0    	ret
