#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to nmea_msgs__msg__Sentence
/// A message representing a single NMEA0183 sentence.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Sentence {
    /// header.stamp is the ROS Time when the sentence was read.
    /// header.frame_id is the frame of reference reported by the satellite
    ///        receiver, usually the location of the antenna.  This is a
    ///        Euclidean frame relative to the vehicle, not a reference
    ///        ellipsoid.
    pub header: std_msgs::msg::Header,

    /// This should only contain ASCII characters in order to be a valid NMEA0183 sentence.
    pub sentence: std::string::String,

}



impl Default for Sentence {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Sentence::default())
  }
}

impl rosidl_runtime_rs::Message for Sentence {
  type RmwMsg = super::msg::rmw::Sentence;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        sentence: msg.sentence.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        sentence: msg.sentence.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      sentence: msg.sentence.to_string(),
    }
  }
}


// Corresponds to nmea_msgs__msg__Gpgga
/// Message from GPGGA NMEA String

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gpgga {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: std::string::String,

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
    pub lat_dir: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lon_dir: std::string::String,


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
    pub altitude_units: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub undulation: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub undulation_units: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub diff_age: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub station_id: std::string::String,

}



impl Default for Gpgga {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Gpgga::default())
  }
}

impl rosidl_runtime_rs::Message for Gpgga {
  type RmwMsg = super::msg::rmw::Gpgga;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
        utc_seconds: msg.utc_seconds,
        lat: msg.lat,
        lon: msg.lon,
        lat_dir: msg.lat_dir.as_str().into(),
        lon_dir: msg.lon_dir.as_str().into(),
        gps_qual: msg.gps_qual,
        num_sats: msg.num_sats,
        hdop: msg.hdop,
        alt: msg.alt,
        altitude_units: msg.altitude_units.as_str().into(),
        undulation: msg.undulation,
        undulation_units: msg.undulation_units.as_str().into(),
        diff_age: msg.diff_age,
        station_id: msg.station_id.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
      utc_seconds: msg.utc_seconds,
      lat: msg.lat,
      lon: msg.lon,
        lat_dir: msg.lat_dir.as_str().into(),
        lon_dir: msg.lon_dir.as_str().into(),
      gps_qual: msg.gps_qual,
      num_sats: msg.num_sats,
      hdop: msg.hdop,
      alt: msg.alt,
        altitude_units: msg.altitude_units.as_str().into(),
      undulation: msg.undulation,
        undulation_units: msg.undulation_units.as_str().into(),
      diff_age: msg.diff_age,
        station_id: msg.station_id.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      message_id: msg.message_id.to_string(),
      utc_seconds: msg.utc_seconds,
      lat: msg.lat,
      lon: msg.lon,
      lat_dir: msg.lat_dir.to_string(),
      lon_dir: msg.lon_dir.to_string(),
      gps_qual: msg.gps_qual,
      num_sats: msg.num_sats,
      hdop: msg.hdop,
      alt: msg.alt,
      altitude_units: msg.altitude_units.to_string(),
      undulation: msg.undulation,
      undulation_units: msg.undulation_units.to_string(),
      diff_age: msg.diff_age,
      station_id: msg.station_id.to_string(),
    }
  }
}


// Corresponds to nmea_msgs__msg__Gpgsa
/// Message from GPGSA NMEA String

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gpgsa {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub auto_manual_mode: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fix_mode: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub sv_ids: Vec<u8>,


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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Gpgsa::default())
  }
}

impl rosidl_runtime_rs::Message for Gpgsa {
  type RmwMsg = super::msg::rmw::Gpgsa;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
        auto_manual_mode: msg.auto_manual_mode.as_str().into(),
        fix_mode: msg.fix_mode,
        sv_ids: msg.sv_ids.into(),
        pdop: msg.pdop,
        hdop: msg.hdop,
        vdop: msg.vdop,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
        auto_manual_mode: msg.auto_manual_mode.as_str().into(),
      fix_mode: msg.fix_mode,
        sv_ids: msg.sv_ids.as_slice().into(),
      pdop: msg.pdop,
      hdop: msg.hdop,
      vdop: msg.vdop,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      message_id: msg.message_id.to_string(),
      auto_manual_mode: msg.auto_manual_mode.to_string(),
      fix_mode: msg.fix_mode,
      sv_ids: msg.sv_ids
          .into_iter()
          .collect(),
      pdop: msg.pdop,
      hdop: msg.hdop,
      vdop: msg.vdop,
    }
  }
}


// Corresponds to nmea_msgs__msg__Gpgst
/// Message from GPGST NMEA String

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gpgst {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: std::string::String,

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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Gpgst::default())
  }
}

impl rosidl_runtime_rs::Message for Gpgst {
  type RmwMsg = super::msg::rmw::Gpgst;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
        utc_seconds: msg.utc_seconds,
        rms: msg.rms,
        semi_major_dev: msg.semi_major_dev,
        semi_minor_dev: msg.semi_minor_dev,
        orientation: msg.orientation,
        lat_dev: msg.lat_dev,
        lon_dev: msg.lon_dev,
        alt_dev: msg.alt_dev,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
      utc_seconds: msg.utc_seconds,
      rms: msg.rms,
      semi_major_dev: msg.semi_major_dev,
      semi_minor_dev: msg.semi_minor_dev,
      orientation: msg.orientation,
      lat_dev: msg.lat_dev,
      lon_dev: msg.lon_dev,
      alt_dev: msg.alt_dev,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      message_id: msg.message_id.to_string(),
      utc_seconds: msg.utc_seconds,
      rms: msg.rms,
      semi_major_dev: msg.semi_major_dev,
      semi_minor_dev: msg.semi_minor_dev,
      orientation: msg.orientation,
      lat_dev: msg.lat_dev,
      lon_dev: msg.lon_dev,
      alt_dev: msg.alt_dev,
    }
  }
}


// Corresponds to nmea_msgs__msg__Gpgsv
/// Total number of satellites in view and data about satellites
/// Because the NMEA sentence is limited to 4 satellites per message, several
/// of these messages may need to be synthesized to get data about all visible
/// satellites.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gpgsv {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: std::string::String,

    /// Number of messages in this sequence
    pub n_msgs: u8,

    /// This messages number in its sequence. The first message is number 1.
    pub msg_number: u8,

    /// Number of satellites currently visible
    pub n_satellites: u8,

    /// Up to 4 satellites are described in each message
    pub satellites: Vec<super::msg::GpgsvSatellite>,

}



impl Default for Gpgsv {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Gpgsv::default())
  }
}

impl rosidl_runtime_rs::Message for Gpgsv {
  type RmwMsg = super::msg::rmw::Gpgsv;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
        n_msgs: msg.n_msgs,
        msg_number: msg.msg_number,
        n_satellites: msg.n_satellites,
        satellites: msg.satellites
          .into_iter()
          .map(|elem| super::msg::GpgsvSatellite::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
      n_msgs: msg.n_msgs,
      msg_number: msg.msg_number,
      n_satellites: msg.n_satellites,
        satellites: msg.satellites
          .iter()
          .map(|elem| super::msg::GpgsvSatellite::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      message_id: msg.message_id.to_string(),
      n_msgs: msg.n_msgs,
      msg_number: msg.msg_number,
      n_satellites: msg.n_satellites,
      satellites: msg.satellites
          .into_iter()
          .map(super::msg::GpgsvSatellite::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to nmea_msgs__msg__GpgsvSatellite
/// Satellite data structure used in GPGSV messages

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::GpgsvSatellite::default())
  }
}

impl rosidl_runtime_rs::Message for GpgsvSatellite {
  type RmwMsg = super::msg::rmw::GpgsvSatellite;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        prn: msg.prn,
        elevation: msg.elevation,
        azimuth: msg.azimuth,
        snr: msg.snr,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      prn: msg.prn,
      elevation: msg.elevation,
      azimuth: msg.azimuth,
      snr: msg.snr,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      prn: msg.prn,
      elevation: msg.elevation,
      azimuth: msg.azimuth,
      snr: msg.snr,
    }
  }
}


// Corresponds to nmea_msgs__msg__Gprmc
/// Message from GPRMC NMEA String

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Gprmc {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub utc_seconds: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub position_status: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lat: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lon: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lat_dir: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lon_dir: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub speed: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub track: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub date: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mag_var: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mag_var_direction: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mode_indicator: std::string::String,

}



impl Default for Gprmc {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Gprmc::default())
  }
}

impl rosidl_runtime_rs::Message for Gprmc {
  type RmwMsg = super::msg::rmw::Gprmc;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
        utc_seconds: msg.utc_seconds,
        position_status: msg.position_status.as_str().into(),
        lat: msg.lat,
        lon: msg.lon,
        lat_dir: msg.lat_dir.as_str().into(),
        lon_dir: msg.lon_dir.as_str().into(),
        speed: msg.speed,
        track: msg.track,
        date: msg.date.as_str().into(),
        mag_var: msg.mag_var,
        mag_var_direction: msg.mag_var_direction.as_str().into(),
        mode_indicator: msg.mode_indicator.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        message_id: msg.message_id.as_str().into(),
      utc_seconds: msg.utc_seconds,
        position_status: msg.position_status.as_str().into(),
      lat: msg.lat,
      lon: msg.lon,
        lat_dir: msg.lat_dir.as_str().into(),
        lon_dir: msg.lon_dir.as_str().into(),
      speed: msg.speed,
      track: msg.track,
        date: msg.date.as_str().into(),
      mag_var: msg.mag_var,
        mag_var_direction: msg.mag_var_direction.as_str().into(),
        mode_indicator: msg.mode_indicator.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      message_id: msg.message_id.to_string(),
      utc_seconds: msg.utc_seconds,
      position_status: msg.position_status.to_string(),
      lat: msg.lat,
      lon: msg.lon,
      lat_dir: msg.lat_dir.to_string(),
      lon_dir: msg.lon_dir.to_string(),
      speed: msg.speed,
      track: msg.track,
      date: msg.date.to_string(),
      mag_var: msg.mag_var,
      mag_var_direction: msg.mag_var_direction.to_string(),
      mode_indicator: msg.mode_indicator.to_string(),
    }
  }
}


