
build/before/opendp-sum-probe:	file format mach-o arm64

Disassembly of section __TEXT,__text:

0000000100003390 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629>:
100003390: f9400829    	ldr	x9, [x1, #0x10]
100003394: b40000e9    	cbz	x9, 0x1000033b0 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0x20>
100003398: f940042a    	ldr	x10, [x1, #0x8]
10000339c: f100113f    	cmp	x9, #0x4
1000033a0: 54000122    	b.hs	0x1000033c4 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0x34>
1000033a4: d280000b    	mov	x11, #0x0               ; =0
1000033a8: 5280000c    	mov	w12, #0x0               ; =0
1000033ac: 14000031    	b	0x100003470 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0xe0>
1000033b0: 5280000c    	mov	w12, #0x0               ; =0
1000033b4: b900090c    	str	w12, [x8, #0x8]
1000033b8: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
1000033bc: f9000109    	str	x9, [x8]
1000033c0: d65f03c0    	ret
1000033c4: f100413f    	cmp	x9, #0x10
1000033c8: 54000082    	b.hs	0x1000033d8 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0x48>
1000033cc: d280000b    	mov	x11, #0x0               ; =0
1000033d0: 5280000c    	mov	w12, #0x0               ; =0
1000033d4: 14000019    	b	0x100003438 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0xa8>
1000033d8: 927ced2b    	and	x11, x9, #0xfffffffffffffff0
1000033dc: 9100814c    	add	x12, x10, #0x20
1000033e0: 6f00e400    	movi.2d	v0, #0000000000000000
1000033e4: aa0b03ed    	mov	x13, x11
1000033e8: 6f00e401    	movi.2d	v1, #0000000000000000
1000033ec: 6f00e402    	movi.2d	v2, #0000000000000000
1000033f0: 6f00e403    	movi.2d	v3, #0000000000000000
1000033f4: ad7f1584    	ldp	q4, q5, [x12, #-0x20]
1000033f8: acc21d86    	ldp	q6, q7, [x12], #0x40
1000033fc: 4ea08480    	add.4s	v0, v4, v0
100003400: 4ea184a1    	add.4s	v1, v5, v1
100003404: 4ea284c2    	add.4s	v2, v6, v2
100003408: 4ea384e3    	add.4s	v3, v7, v3
10000340c: f10041ad    	subs	x13, x13, #0x10
100003410: 54ffff21    	b.ne	0x1000033f4 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0x64>
100003414: 4ea08420    	add.4s	v0, v1, v0
100003418: 4ea08440    	add.4s	v0, v2, v0
10000341c: 4ea08460    	add.4s	v0, v3, v0
100003420: 4eb1b800    	addv.4s	s0, v0
100003424: 1e26000c    	fmov	w12, s0
100003428: eb0b013f    	cmp	x9, x11
10000342c: 540002e0    	b.eq	0x100003488 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0xf8>
100003430: f27e053f    	tst	x9, #0xc
100003434: 540001e0    	b.eq	0x100003470 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0xe0>
100003438: aa0b03ed    	mov	x13, x11
10000343c: 927ef52b    	and	x11, x9, #0xfffffffffffffffc
100003440: 6f00e400    	movi.2d	v0, #0000000000000000
100003444: 4e041d80    	mov.s	v0[0], w12
100003448: cb0b01ac    	sub	x12, x13, x11
10000344c: 8b0d094d    	add	x13, x10, x13, lsl #2
100003450: 3cc105a1    	ldr	q1, [x13], #0x10
100003454: 4ea08420    	add.4s	v0, v1, v0
100003458: b100118c    	adds	x12, x12, #0x4
10000345c: 54ffffa1    	b.ne	0x100003450 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0xc0>
100003460: 4eb1b800    	addv.4s	s0, v0
100003464: 1e26000c    	fmov	w12, s0
100003468: eb0b013f    	cmp	x9, x11
10000346c: 540000e0    	b.eq	0x100003488 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0xf8>
100003470: cb0b0129    	sub	x9, x9, x11
100003474: 8b0b094a    	add	x10, x10, x11, lsl #2
100003478: b840454b    	ldr	w11, [x10], #0x4
10000347c: 0b0c016c    	add	w12, w11, w12
100003480: f1000529    	subs	x9, x9, #0x1
100003484: 54ffffa1    	b.ne	0x100003478 <opendp::core::Function$LT$DI$C$DO$GT$::new::_$u7b$$u7b$closure$u7d$$u7d$::had1d22e328927629+0xe8>
100003488: b900090c    	str	w12, [x8, #0x8]
10000348c: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
100003490: f9000109    	str	x9, [x8]
100003494: d65f03c0    	ret


build/before/opendp-sum-probe:	file format mach-o arm64

Disassembly of section __TEXT,__text:

0000000100003538 <opendp::core::StabilityRelation$LT$MI$C$MO$GT$::new_from_constant::_$u7b$$u7b$closure$u7d$$u7d$::h4ecfffe7d59d56ae>:
100003538: d10143ff    	sub	sp, sp, #0x50
10000353c: a9034ff4    	stp	x20, x19, [sp, #0x30]
100003540: a9047bfd    	stp	x29, x30, [sp, #0x40]
100003544: 910103fd    	add	x29, sp, #0x40
100003548: aa0003f4    	mov	x20, x0
10000354c: aa0803f3    	mov	x19, x8
100003550: b9400020    	ldr	w0, [x1]
100003554: 910003e8    	mov	x8, sp
100003558: 94000120    	bl	0x1000039d8 <_$LT$i32$u20$as$u20$opendp..traits..InfCast$LT$u32$GT$$GT$::inf_cast::hfdba746729608afb>
10000355c: f94003e8    	ldr	x8, [sp]
100003560: b9400be9    	ldr	w9, [sp, #0x8]
100003564: b24107ea    	mov	x10, #-0x7fffffffffffffff ; =-9223372036854775807
100003568: eb0a011f    	cmp	x8, x10
10000356c: 54000121    	b.ne	0x100003590 <opendp::core::StabilityRelation$LT$MI$C$MO$GT$::new_from_constant::_$u7b$$u7b$closure$u7d$$u7d$::h4ecfffe7d59d56ae+0x58>
100003570: b940028a    	ldr	w10, [x20]
100003574: 1b097d49    	mul	w9, w10, w9
100003578: b9000a69    	str	w9, [x19, #0x8]
10000357c: f9000268    	str	x8, [x19]
100003580: a9447bfd    	ldp	x29, x30, [sp, #0x40]
100003584: a9434ff4    	ldp	x20, x19, [sp, #0x30]
100003588: 910143ff    	add	sp, sp, #0x50
10000358c: d65f03c0    	ret
100003590: 3cc0c3e0    	ldur	q0, [sp, #0xc]
100003594: 3c80c260    	stur	q0, [x19, #0xc]
100003598: 3cc1c3e0    	ldur	q0, [sp, #0x1c]
10000359c: 3c81c260    	stur	q0, [x19, #0x1c]
1000035a0: b9402fea    	ldr	w10, [sp, #0x2c]
1000035a4: b9002e6a    	str	w10, [x19, #0x2c]
1000035a8: b9000a69    	str	w9, [x19, #0x8]
1000035ac: f9000268    	str	x8, [x19]
1000035b0: a9447bfd    	ldp	x29, x30, [sp, #0x40]
1000035b4: a9434ff4    	ldp	x20, x19, [sp, #0x30]
1000035b8: 910143ff    	add	sp, sp, #0x50
1000035bc: d65f03c0    	ret


build/before/opendp-sum-probe:	file format mach-o arm64

Disassembly of section __TEXT,__text:

00000001000039d8 <_$LT$i32$u20$as$u20$opendp..traits..InfCast$LT$u32$GT$$GT$::inf_cast::hfdba746729608afb>:
1000039d8: 14000002    	b	0x1000039e0 <_$LT$i32$u20$as$u20$opendp..traits..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h83edbc8cf4458b47>


build/before/opendp-sum-probe:	file format mach-o arm64

Disassembly of section __TEXT,__text:

00000001000039e0 <_$LT$i32$u20$as$u20$opendp..traits..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h83edbc8cf4458b47>:
1000039e0: d10203ff    	sub	sp, sp, #0x80
1000039e4: a90367fa    	stp	x26, x25, [sp, #0x30]
1000039e8: a9045ff8    	stp	x24, x23, [sp, #0x40]
1000039ec: a90557f6    	stp	x22, x21, [sp, #0x50]
1000039f0: a9064ff4    	stp	x20, x19, [sp, #0x60]
1000039f4: a9077bfd    	stp	x29, x30, [sp, #0x70]
1000039f8: 9101c3fd    	add	x29, sp, #0x70
1000039fc: 37f800a0    	tbnz	w0, #0x1f, 0x100003a10 <_$LT$i32$u20$as$u20$opendp..traits..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h83edbc8cf4458b47+0x30>
100003a00: b9000900    	str	w0, [x8, #0x8]
100003a04: b24107e9    	mov	x9, #-0x7fffffffffffffff ; =-9223372036854775807
100003a08: f9000109    	str	x9, [x8]
100003a0c: 1400002d    	b	0x100003ac0 <_$LT$i32$u20$as$u20$opendp..traits..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h83edbc8cf4458b47+0xe0>
100003a10: aa0803f9    	mov	x25, x8
100003a14: 9100bfe8    	add	x8, sp, #0x2f
100003a18: 90000009    	adrp	x9, 0x100003000 <core::ptr::drop_in_place$LT$opendp..error..Error$GT$::h6d983e4ede50f9d6+0x18>
100003a1c: 91336129    	add	x9, x9, #0xcd8
100003a20: a901a7e8    	stp	x8, x9, [sp, #0x18]
100003a24: b0000200    	adrp	x0, 0x100044000 <core::unicode::unicode_data::grapheme_extend::SHORT_OFFSET_RUNS::h068fceb00e1a42b2+0xcc>
100003a28: 91228c00    	add	x0, x0, #0x8a3
100003a2c: 910003e8    	mov	x8, sp
100003a30: 910063e1    	add	x1, sp, #0x18
100003a34: 9400cce8    	bl	0x100036dd4 <alloc::fmt::format::format_inner::hd571df24e790cabc>
100003a38: f9400bf3    	ldr	x19, [sp, #0x10]
100003a3c: b6f800b3    	tbz	x19, #0x3f, 0x100003a50 <_$LT$i32$u20$as$u20$opendp..traits..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h83edbc8cf4458b47+0x70>
100003a40: d2800017    	mov	x23, #0x0               ; =0
100003a44: aa1703e0    	mov	x0, x23
100003a48: aa1303e1    	mov	x1, x19
100003a4c: 9400f2af    	bl	0x100040508 <alloc::raw_vec::handle_error::hd9deaf7dc19ebb3f>
100003a50: a94057f4    	ldp	x20, x21, [sp]
100003a54: b4000133    	cbz	x19, 0x100003a78 <_$LT$i32$u20$as$u20$opendp..traits..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h83edbc8cf4458b47+0x98>
100003a58: 97ffffd7    	bl	0x1000039b4 <__rustc::__rust_no_alloc_shim_is_unstable_v2>
100003a5c: 52800037    	mov	w23, #0x1               ; =1
100003a60: aa1303e0    	mov	x0, x19
100003a64: 52800021    	mov	w1, #0x1                ; =1
100003a68: 97ffffcf    	bl	0x1000039a4 <__rustc::__rust_alloc>
100003a6c: b4fffec0    	cbz	x0, 0x100003a44 <_$LT$i32$u20$as$u20$opendp..traits..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h83edbc8cf4458b47+0x64>
100003a70: aa0003f6    	mov	x22, x0
100003a74: 14000002    	b	0x100003a7c <_$LT$i32$u20$as$u20$opendp..traits..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h83edbc8cf4458b47+0x9c>
100003a78: 52800036    	mov	w22, #0x1               ; =1
100003a7c: aa1603e0    	mov	x0, x22
100003a80: aa1503e1    	mov	x1, x21
100003a84: aa1303e2    	mov	x2, x19
100003a88: 9400f464    	bl	0x100040c18 <dyld_stub_binder+0x100040c18>
100003a8c: 94000388    	bl	0x1000048ac <backtrace::capture::Backtrace::new_unresolved::h1fabcc9010bc1e2d>
100003a90: aa0003f7    	mov	x23, x0
100003a94: aa0103f8    	mov	x24, x1
100003a98: b40000b4    	cbz	x20, 0x100003aac <_$LT$i32$u20$as$u20$opendp..traits..ExactIntCast$LT$u32$GT$$GT$::exact_int_cast::h83edbc8cf4458b47+0xcc>
100003a9c: aa1503e0    	mov	x0, x21
100003aa0: aa1403e1    	mov	x1, x20
100003aa4: 52800022    	mov	w2, #0x1                ; =1
100003aa8: 97ffffc0    	bl	0x1000039a8 <__rustc::__rust_dealloc>
100003aac: a9005b33    	stp	x19, x22, [x25]
100003ab0: a9015f33    	stp	x19, x23, [x25, #0x10]
100003ab4: f9001338    	str	x24, [x25, #0x20]
100003ab8: 528000a8    	mov	w8, #0x5                ; =5
100003abc: 3900a328    	strb	w8, [x25, #0x28]
100003ac0: a9477bfd    	ldp	x29, x30, [sp, #0x70]
100003ac4: a9464ff4    	ldp	x20, x19, [sp, #0x60]
100003ac8: a94557f6    	ldp	x22, x21, [sp, #0x50]
100003acc: a9445ff8    	ldp	x24, x23, [sp, #0x40]
100003ad0: a94367fa    	ldp	x26, x25, [sp, #0x30]
100003ad4: 910203ff    	add	sp, sp, #0x80
100003ad8: d65f03c0    	ret
