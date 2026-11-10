use opendp::core::Domain;
use opendp::error::Fallible;

#[unsafe(no_mangle)]
#[inline(never)]
extern "C" fn probe_anchor() {}

fn print_closure<T>(label: &str, closure: &dyn Fn(&T) -> Fallible<i32>) {
    // Compiler-specific fixture for the linked arm64 Mach-O. The extractor also
    // checks that the reported call slot resolves to an OpenDP closure symbol.
    let (data, vtable): (*const u8, *const usize) =
        unsafe { std::mem::transmute(closure) };
    let (size, entry) = unsafe { (*vtable.add(1), *vtable.add(5)) };
    let anchor = probe_anchor as *const () as usize;
    let delta = entry as isize - anchor as isize;
    match size {
        0 => println!("fixture {label} {delta} empty"),
        4 => {
            let capture = unsafe { data.cast::<i32>().read_unaligned() };
            println!("fixture {label} {delta} {capture}");
        }
        _ => panic!("unexpected closure payload size {size}"),
    }
}

fn print_vec_layout(row: &Vec<i32>) {
    // On the pinned compiler this Vec has three initialized machine words.
    // Distinct length and capacity let us identify the slots independently.
    assert_eq!(std::mem::size_of::<Vec<i32>>(), 24);
    let raw = row as *const Vec<i32> as *const usize;
    let words = unsafe { [raw.read(), raw.add(1).read(), raw.add(2).read()] };
    let index = |v| words.iter().position(|&w| w == v).unwrap();
    println!(
        "fixture vec {} {} {}",
        index(row.capacity()), index(row.as_ptr() as usize), index(row.len())
    );
}
use opendp::trans::make_sized_bounded_sum;

fn main() {
    let transform = make_sized_bounded_sum::<i32>(2, (0, 3)).unwrap();
    let map = transform.stability_relation.forward_map.as_ref().unwrap();
    let bounds = [0, 1, 2, 3, 4].map(|d| map(&d).unwrap());
    print_closure("sum", transform.function.function.as_ref());
    print_closure("bound", map.as_ref());
    let mut layout_sample = Vec::with_capacity(8);
    layout_sample.extend([0, 3]);
    print_vec_layout(&layout_sample);
    let left = vec![0, 0];
    let right = vec![0, 3];
    assert!(transform.input_domain.member(&left).unwrap());
    assert!(transform.input_domain.member(&right).unwrap());
    assert_eq!(transform.invoke(&left).unwrap(), 0);
    assert_eq!(transform.invoke(&right).unwrap(), 3);
    println!(
        "bounds for distances [0, 1, 2, 3, 4]: {bounds:?}; witness sums: [0, 3]; check(2, 2): {}",
        transform.check(&2, &2).unwrap()
    );

    let rows: Vec<_> = (0..=3).flat_map(|a| (0..=3).map(move |b| vec![a, b])).collect();
    let mut violations = 0;
    for x in &rows {
        for y in &rows {
            assert!(transform.input_domain.member(x).unwrap());
            assert!(transform.input_domain.member(y).unwrap());
            let shared = (0..=3)
                .map(|value| {
                    let count = |row: &Vec<i32>| row.iter().filter(|&&v| v == value).count();
                    count(x).min(count(y))
                })
                .sum::<usize>();
            let distance = 2 * (2 - shared);
            let change = transform.invoke(x).unwrap().abs_diff(transform.invoke(y).unwrap());
            violations += usize::from(change > bounds[distance] as u32);
        }
    }
    println!("{violations} sensitivity violations in 256 ordered pairs");
    if cfg!(feature = "historical_bug") {
        assert_eq!(bounds, [0, 1, 2, 3, 4]);
        assert!(transform.check(&2, &2).unwrap());
        assert!(violations > 0);
    } else {
        assert_eq!(bounds, [0, 0, 3, 3, 6]);
        assert!(!transform.check(&2, &2).unwrap());
        assert_eq!(violations, 0);
    }
}
