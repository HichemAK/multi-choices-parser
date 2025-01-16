use pyo3::prelude::*;
mod trie;

#[pyfunction]
fn hello_from_bin() -> String {
    "Hello from multi-choices-parser!".to_string()
}

#[pyclass]
struct MultiChoicesParser {

}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_from_bin, m)?)?;
    m.add_class::<MultiChoicesParser>()?;
    Ok(())
}
