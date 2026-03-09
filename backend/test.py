import pydicom

ds = pydicom.dcmread("C:/Users/DeveshSoni/Downloads/dicom_00023075_033.dcm")
print("dtype:", ds.pixel_array.dtype)
print("BitsAllocated:", ds.BitsAllocated)
print("BitsStored:", ds.BitsStored)
print("pixel min/max:", ds.pixel_array.min(), ds.pixel_array.max())
