#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "nmea_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Sentence() -> *const std::ffi::c_void;
}

#[link(name = "nmea_msgs__rosidl_generator_c")]
extern "C" {
    fn nmea_msgs__msg__Sentence__init(msg: *mut Sentence) -> bool;
    fn nmea_msgs__msg__Sentence__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Sentence>, size: usize) -> bool;
    fn nmea_msgs__msg__Sentence__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Sentence>);
    fn nmea_msgs__msg__Sentence__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Sentence>, out_seq: *mut rosidl_runtime_rs::Sequence<Sentence>) -> bool;
}

// Corresponds to nmea_msgs__msg__Sentence
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// A message representing a single NMEA0183 sentence.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Sentence {
    /// header.stamp is the ROS Time when the sentence was read.
    /// header.frame_id is the frame of reference reported by the satellite
    ///        receiver, usually the location of the antenna.  This is a
    ///        Euclidean frame relative to the vehicle, not a reference
    ///        ellipsoid.
    pub header: std_msgs::msg::rmw::Header,

    /// This should only contain ASCII characters in order to be a valid NMEA0183 sentence.
    pub sentence: rosidl_runtime_rs::String,

}



impl Default for Sentence {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !nmea_msgs__msg__Sentence__init(&mut msg as *mut _) {
        panic!("Call to nmea_msgs__msg__Sentence__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Sentence {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Sentence__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Sentence__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Sentence__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Sentence {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Sentence where Self: Sized {
  const TYPE_NAME: &'static str = "nmea_msgs/msg/Sentence";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Sentence() }
  }
}


#[link(name = "nmea_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gpgga() -> *const std::ffi::c_void;
}

#[link(name = "nmea_msgs__rosidl_generator_c")]
extern "C" {
    fn nmea_msgs__msg__Gpgga__init(msg: *mut Gpgga) -> bool;
    fn nmea_msgs__msg__Gpgga__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Gpgga>, size: usize) -> bool;
    fn nmea_msgs__msg__Gpgga__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Gpgga>);
    fn nmea_msgs__msg__Gpgga__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Gpgga>, out_seq: *mut rosidl_runtime_rs::Sequence<Gpgga>) -> bool;
}

// Corresponds to nmea_msgs__msg__Gpgga
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Message from GPGGA NMEA String

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gpgga {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: rosidl_runtime_rs::String,

    /// UTC seconds from midnight
    pub utc_seconds: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lat: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lon: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lat_dir: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lon_dir: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub gps_qual: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub num_sats: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub hdop: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub alt: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub altitude_units: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub undulation: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub undulation_units: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub diff_age: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub station_id: rosidl_runtime_rs::String,

}



impl Default for Gpgga {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !nmea_msgs__msg__Gpgga__init(&mut msg as *mut _) {
        panic!("Call to nmea_msgs__msg__Gpgga__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Gpgga {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgga__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgga__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgga__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Gpgga {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Gpgga where Self: Sized {
  const TYPE_NAME: &'static str = "nmea_msgs/msg/Gpgga";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gpgga() }
  }
}


#[link(name = "nmea_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gpgsa() -> *const std::ffi::c_void;
}

#[link(name = "nmea_msgs__rosidl_generator_c")]
extern "C" {
    fn nmea_msgs__msg__Gpgsa__init(msg: *mut Gpgsa) -> bool;
    fn nmea_msgs__msg__Gpgsa__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Gpgsa>, size: usize) -> bool;
    fn nmea_msgs__msg__Gpgsa__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Gpgsa>);
    fn nmea_msgs__msg__Gpgsa__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Gpgsa>, out_seq: *mut rosidl_runtime_rs::Sequence<Gpgsa>) -> bool;
}

// Corresponds to nmea_msgs__msg__Gpgsa
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Message from GPGSA NMEA String

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gpgsa {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub auto_manual_mode: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fix_mode: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub sv_ids: rosidl_runtime_rs::Sequence<u8>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pdop: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub hdop: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub vdop: f32,

}



impl Default for Gpgsa {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !nmea_msgs__msg__Gpgsa__init(&mut msg as *mut _) {
        panic!("Call to nmea_msgs__msg__Gpgsa__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Gpgsa {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgsa__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgsa__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgsa__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Gpgsa {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Gpgsa where Self: Sized {
  const TYPE_NAME: &'static str = "nmea_msgs/msg/Gpgsa";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gpgsa() }
  }
}


#[link(name = "nmea_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gpgst() -> *const std::ffi::c_void;
}

#[link(name = "nmea_msgs__rosidl_generator_c")]
extern "C" {
    fn nmea_msgs__msg__Gpgst__init(msg: *mut Gpgst) -> bool;
    fn nmea_msgs__msg__Gpgst__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Gpgst>, size: usize) -> bool;
    fn nmea_msgs__msg__Gpgst__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Gpgst>);
    fn nmea_msgs__msg__Gpgst__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Gpgst>, out_seq: *mut rosidl_runtime_rs::Sequence<Gpgst>) -> bool;
}

// Corresponds to nmea_msgs__msg__Gpgst
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Message from GPGST NMEA String

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gpgst {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: rosidl_runtime_rs::String,

    /// UTC seconds from midnight
    pub utc_seconds: f64,

    /// Root-Mean-Squared value of standard deviation of range inputs
    pub rms: f32,

    /// Standard Deviations of semi-major and minor axes of error ellipse
    pub semi_major_dev: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub semi_minor_dev: f32,

    /// Orientation of the semi-major axis of error ellipse with respect to true north
    pub orientation: f32,

    /// Standard Deviations of latitude, longitude, and altitude measurements
    pub lat_dev: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lon_dev: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub alt_dev: f32,

}



impl Default for Gpgst {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !nmea_msgs__msg__Gpgst__init(&mut msg as *mut _) {
        panic!("Call to nmea_msgs__msg__Gpgst__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Gpgst {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgst__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgst__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgst__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Gpgst {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Gpgst where Self: Sized {
  const TYPE_NAME: &'static str = "nmea_msgs/msg/Gpgst";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gpgst() }
  }
}


#[link(name = "nmea_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gpgsv() -> *const std::ffi::c_void;
}

#[link(name = "nmea_msgs__rosidl_generator_c")]
extern "C" {
    fn nmea_msgs__msg__Gpgsv__init(msg: *mut Gpgsv) -> bool;
    fn nmea_msgs__msg__Gpgsv__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Gpgsv>, size: usize) -> bool;
    fn nmea_msgs__msg__Gpgsv__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Gpgsv>);
    fn nmea_msgs__msg__Gpgsv__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Gpgsv>, out_seq: *mut rosidl_runtime_rs::Sequence<Gpgsv>) -> bool;
}

// Corresponds to nmea_msgs__msg__Gpgsv
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Total number of satellites in view and data about satellites
/// Because the NMEA sentence is limited to 4 satellites per message, several
/// of these messages may need to be synthesized to get data about all visible
/// satellites.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gpgsv {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: rosidl_runtime_rs::String,

    /// Number of messages in this sequence
    pub n_msgs: u8,

    /// This messages number in its sequence. The first message is number 1.
    pub msg_number: u8,

    /// Number of satellites currently visible
    pub n_satellites: u8,

    /// Up to 4 satellites are described in each message
    pub satellites: rosidl_runtime_rs::Sequence<super::super::msg::rmw::GpgsvSatellite>,

}



impl Default for Gpgsv {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !nmea_msgs__msg__Gpgsv__init(&mut msg as *mut _) {
        panic!("Call to nmea_msgs__msg__Gpgsv__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Gpgsv {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgsv__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgsv__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gpgsv__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Gpgsv {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Gpgsv where Self: Sized {
  const TYPE_NAME: &'static str = "nmea_msgs/msg/Gpgsv";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gpgsv() }
  }
}


#[link(name = "nmea_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__GpgsvSatellite() -> *const std::ffi::c_void;
}

#[link(name = "nmea_msgs__rosidl_generator_c")]
extern "C" {
    fn nmea_msgs__msg__GpgsvSatellite__init(msg: *mut GpgsvSatellite) -> bool;
    fn nmea_msgs__msg__GpgsvSatellite__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GpgsvSatellite>, size: usize) -> bool;
    fn nmea_msgs__msg__GpgsvSatellite__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GpgsvSatellite>);
    fn nmea_msgs__msg__GpgsvSatellite__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GpgsvSatellite>, out_seq: *mut rosidl_runtime_rs::Sequence<GpgsvSatellite>) -> bool;
}

// Corresponds to nmea_msgs__msg__GpgsvSatellite
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Satellite data structure used in GPGSV messages

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GpgsvSatellite {
    /// PRN number of the satellite
    /// GPS = 1..32
    /// SBAS = 33..64
    /// GLO = 65..96
    pub prn: u8,

    /// Elevation, degrees. Maximum 90
    pub elevation: u8,

    /// Azimuth, True North degrees. [0, 359]
    pub azimuth: u16,

    /// Signal to noise ratio, 0-99 dB. -1 when null in NMEA sentence (not tracking)
    pub snr: i8,

}



impl Default for GpgsvSatellite {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !nmea_msgs__msg__GpgsvSatellite__init(&mut msg as *mut _) {
        panic!("Call to nmea_msgs__msg__GpgsvSatellite__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GpgsvSatellite {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__GpgsvSatellite__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__GpgsvSatellite__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__GpgsvSatellite__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GpgsvSatellite {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GpgsvSatellite where Self: Sized {
  const TYPE_NAME: &'static str = "nmea_msgs/msg/GpgsvSatellite";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__GpgsvSatellite() }
  }
}


#[link(name = "nmea_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gprmc() -> *const std::ffi::c_void;
}

#[link(name = "nmea_msgs__rosidl_generator_c")]
extern "C" {
    fn nmea_msgs__msg__Gprmc__init(msg: *mut Gprmc) -> bool;
    fn nmea_msgs__msg__Gprmc__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Gprmc>, size: usize) -> bool;
    fn nmea_msgs__msg__Gprmc__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Gprmc>);
    fn nmea_msgs__msg__Gprmc__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Gprmc>, out_seq: *mut rosidl_runtime_rs::Sequence<Gprmc>) -> bool;
}

// Corresponds to nmea_msgs__msg__Gprmc
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Message from GPRMC NMEA String

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gprmc {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub utc_seconds: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub position_status: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lat: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lon: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lat_dir: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lon_dir: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub speed: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub track: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub date: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mag_var: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mag_var_direction: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mode_indicator: rosidl_runtime_rs::String,

}



impl Default for Gprmc {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !nmea_msgs__msg__Gprmc__init(&mut msg as *mut _) {
        panic!("Call to nmea_msgs__msg__Gprmc__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Gprmc {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gprmc__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gprmc__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { nmea_msgs__msg__Gprmc__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Gprmc {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Gprmc where Self: Sized {
  const TYPE_NAME: &'static str = "nmea_msgs/msg/Gprmc";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__nmea_msgs__msg__Gprmc() }
  }
}


