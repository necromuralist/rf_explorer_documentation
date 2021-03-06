RFE Sweep Data
==============

.. currentmodule:: RFExplorer.RFESweepData

The :class:`RFESweepData` holds the data for a single sweep of the spectrum (I think).

.. autosummary::
   :toctree: autogenerated_api

   RFESweepData

Get The Peak
------------

The first example given by the code uses the *Peak Step* to print out some information. The *Peak Step* is the frequency that had the largest amplitude for that sweep. The ``GetPeakStep`` will return the index (step) that matches the peak which you can then use to make some queries.

.. autosummary::
   :toctree: autogenerated_api

   RFESweepData.GetPeakStep
   RFESweepData.GetAmplitude_DBM
   RFESweepData.GetFrequencyMHZ

.. code::

   peak_step = sweep_data.GetPeakStep()
   peak_amplitude = sweep_data.GetAmplitude_DBM(peak_step)
   peak_frequency = sweep_data.GetFrequencyMHZ(peak_step)

CSV Output
----------

These methods will dump the sweep data with a (quasi) CSV-format.

.. autosummary::
   :toctree: autogenerated_api

   RFESweepData.Dump
   RFESweepData.SaveFileCSV

.. note:: When the :class:`RFESweepData` is instantiated it sets a :meth:`datetime.datetime.now` value in an attribute named ``self.m_Time`` which might be useful when constructing your own CSV. Or use :attr:`RFESweepData.CaptureTime` which is the same thing.
